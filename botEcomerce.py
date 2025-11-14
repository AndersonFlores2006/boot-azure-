import json
import os

import pyodbc
import requests
from flask import Flask, jsonify, render_template, request

# Cargar variables de entorno desde archivo .env
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # Si no está instalado python-dotenv, se usará os.getenv() sin un archivo .env
    pass

# --- Inicialización de la App Flask ---
app = Flask(__name__)

# --- Configuración de Azure Cognitive Services ---
SUBSCRIPTION_KEY = os.getenv("COGNITIVE_SERVICES_KEY")
ENDPOINT_URL = "https://chatbotlanguajefinal.cognitiveservices.azure.com/language/:analyze-conversations?api-version=2024-11-15-preview"
PROJECT_NAME = os.getenv("PROJECT_NAME", "chatbot-final")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "ChatbotEcomerce")

# --- Configuración de Base de Datos ---
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = "{ODBC Driver 17 for SQL Server}"

# Modo de depuración de la base de datos (se controla por .env)
DEBUG_DB = os.getenv("DEBUG_DB", "false").lower() == "true"


# --- Memoria del Chatbot (simplificado para este ejemplo) ---
conversation_state = {}


# --- Lógica del Bot (funciones adaptadas) ---
def get_clu_analysis(query):
    if not SUBSCRIPTION_KEY:
        print("Error: COGNITIVE_SERVICES_KEY no está configurada.")
        return None

    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Apim-Request-Id": "4ffcac1c-b2fc-48ba-bd6d-b69d9942995a",
        "Content-Type": "application/json",
    }
    payload = {
        "kind": "Conversation",
        "analysisInput": {
            "conversationItem": {
                "id": "user-1",
                "text": query,
                "modality": "text",
                "language": "es",
                "participantId": "user-1",
            }
        },
        "parameters": {
            "projectName": PROJECT_NAME,
            "verbose": True,
            "deploymentName": DEPLOYMENT_NAME,
            "stringIndexType": "TextElement_V8",
        },
    }
    try:
        response = requests.post(ENDPOINT_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # En lugar de un print, puedes loggear esto con un sistema de logging real en producción
        print(f"Error al conectar con el servicio CLU: {e}")
        return None


def convert_to_int(text_value):
    if isinstance(text_value, int):
        return text_value
    text_value = str(text_value).lower()
    num_words = {
        "un": 1,
        "uno": 1,
        "una": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
    }
    if text_value in num_words:
        return num_words[text_value]
    try:
        return int(text_value)
    except (ValueError, TypeError):
        return None


def execute_db_query(query, params=(), fetch=None):
    if not all([DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD]):
        print("Error: Las credenciales de la base de datos no están configuradas.")
        return None
    try:
        conn_str = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "all":
                    return cursor.fetchall()
                else:
                    conn.commit()  # Para INSERT, UPDATE, DELETE
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # Mensaje de error simplificado para no exponer demasiada info en logs normales
        # En un entorno de producción, se usaría un logger más sofisticado.
        print(f"Error de base de datos: {sqlstate}\n{ex}")
        return None


def handle_crear_pedido(state, entities, user_input):
    waiting_for_payment = state.get("Producto") and not state.get("MetodoPago")
    payment_keywords = ["yape", "tarjeta", "efectivo", "transferencia"]
    for entity in entities:
        if (
            waiting_for_payment
            and entity["category"] == "Producto"
            and entity["text"].lower() in payment_keywords
        ):
            continue
        state[entity["category"]] = entity["text"]

    producto = state.get("Producto")
    cantidad_texto = state.get("Cantidad", "1")
    metodo_pago = state.get("MetodoPago")

    if not metodo_pago:
        for keyword in payment_keywords:
            if keyword in user_input.lower():
                metodo_pago = keyword
                state["MetodoPago"] = keyword
                break

    if not producto:
        return ("No entendí qué producto deseas. Por favor, sé más específico.", {})

    cantidad_num = convert_to_int(cantidad_texto)
    if cantidad_num is None:
        return (f"No pude interpretar '{cantidad_texto}' como una cantidad válida.", {})

    if not metodo_pago:
        return (
            "Por favor, especifica un método de pago (ej. tarjeta, yape, efectivo).",
            state,
        )

    sql = "INSERT INTO Pedidos (Producto, Cantidad, MetodoPago) OUTPUT INSERTED.Id VALUES (?, ?, ?);"
    params = (producto, cantidad_num, metodo_pago)
    result = execute_db_query(sql, params, fetch="one")

    if result:
        new_id = result[0]
        response_text = f"¡Perfecto! He creado tu pedido de {cantidad_num} {producto} con {metodo_pago}. Tu número de pedido es {new_id}."
        return (response_text, {})
    else:
        return ("Lo siento, hubo un problema al crear tu pedido.", {})


def handle_consultar_pedido(entities):
    id_pedido_text = next(
        (e["text"] for e in entities if e["category"] == "IdPedido"), None
    )
    if id_pedido_text:
        id_pedido = "".join(filter(str.isdigit, id_pedido_text))
    else:
        id_pedido = None

    if not id_pedido:
        return "No entendí qué número de pedido quieres consultar."

    sql = "SELECT Estado, Producto FROM Pedidos WHERE Id = ?;"
    result = execute_db_query(sql, (id_pedido,), fetch="one")

    if result:
        return f"El estado de tu pedido #{id_pedido} ({result[1]}) es: {result[0]}."
    else:
        return f"No pude encontrar el pedido con el ID {id_pedido}."


def handle_pagar_pedido(entities):
    id_pedido_text = next(
        (e["text"] for e in entities if e["category"] == "IdPedido"), None
    )
    if id_pedido_text:
        id_pedido = "".join(filter(str.isdigit, id_pedido_text))
    else:
        id_pedido = None

    if not id_pedido:
        return "Por favor, dime el número del pedido que quieres pagar."

    check_sql = "SELECT Estado FROM Pedidos WHERE Id = ?;"
    result = execute_db_query(check_sql, (id_pedido,), fetch="one")

    if not result:
        return f"No pude encontrar el pedido con el ID {id_pedido}."
    if result[0] == "Pagado":
        return f"El pedido #{id_pedido} ya se encuentra pagado."

    update_sql = "UPDATE Pedidos SET Estado = 'Pagado' WHERE Id = ?;"
    execute_db_query(update_sql, (id_pedido,))
    return f"¡Gracias! Se ha registrado el pago para el pedido #{id_pedido}."


def normalize_keyword(keyword):
    """Normaliza una palabra a su forma singular para la búsqueda en la BD."""
    keyword = keyword.lower()
    # Reglas simples de pluralización para este caso de uso
    if keyword.endswith("es"):
        # Ej: "horarios" -> "horario", "devoluciones" -> "devolucion"
        # (Asume que la 's' final no es parte de la palabra original)
        if keyword[:-2] in ["horario", "devolucion", "envio"]:
             return keyword[:-2]
    if keyword.endswith("s"):
        # Ej: "garantías" -> "garantía"
        if keyword[:-1] in ["garantia", "envio", "horario", "devolucione"]:
            return keyword[:-1]
    return keyword


def handle_preguntas_frecuentes(entities):
    """Busca una respuesta a una pregunta frecuente en la base de datos."""
    tema_original = next(
        (e["text"] for e in entities if e["category"] == "TemaPregunta"), None
    )

    if not tema_original:
        return "Tengo respuestas a preguntas sobre horarios, envíos, devoluciones, garantía y métodos de pago. ¿Sobre qué te gustaría saber?"

    # Normaliza el tema para que coincida con la palabra clave (ej. "horarios" -> "horario")
    tema_normalizado = normalize_keyword(tema_original)

    # Se utiliza COLLATE para que la búsqueda no distinga entre acentos (ej. "envio" vs "envío")
    sql = "SELECT Respuesta FROM PreguntasFrecuentes WHERE PalabraClave COLLATE Latin1_General_CI_AI LIKE ? COLLATE Latin1_General_CI_AI;"
    param = f"%{tema_normalizado}%"
    result = execute_db_query(sql, (param,), fetch="one")

    if result:
        return result[0]
    else:
        return f"No encontré una respuesta específica sobre '{tema_original}'. Puedo ayudarte con temas como horarios, envíos, devoluciones, garantía o métodos de pago."


# --- Rutas de la API ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global conversation_state
    user_message = request.json["message"]

    analysis = get_clu_analysis(user_message)
    bot_response = "Lo siento, no entendí eso."

    if analysis:
        prediction = analysis.get("result", {}).get("prediction", {})
        top_intent = prediction.get("topIntent")
        entities = prediction.get("entities", [])

        # --- Red de Seguridad para Intenciones ---
        query_keywords = ["estado", "está", "cómo va", "situación"]
        if any(keyword in user_message.lower() for keyword in query_keywords):
            top_intent = "ConsultarPedido"

        # Red de seguridad para Preguntas Frecuentes para mejorar la precisión
        faq_keywords = [
            "horario",
            "envío",
            "devolución",
            "garantía",
            "pago",
            "política de",
            "información sobre",
            "atienden",
            "aceptan",
        ]
        # Si el mensaje parece una pregunta y no una orden directa
        if any(keyword in user_message.lower() for keyword in faq_keywords):
            is_order = top_intent == "CrearPedido" and any(
                e["category"] == "Producto" for e in entities
            )
            if not is_order:
                top_intent = "PreguntasFrecuentes"

        if top_intent == "CrearPedido" or conversation_state:
            bot_response, conversation_state = handle_crear_pedido(
                conversation_state, entities, user_message
            )
        elif top_intent == "ConsultarPedido":
            bot_response = handle_consultar_pedido(entities)
            conversation_state = {}
        elif top_intent == "PagarPedido":
            bot_response = handle_pagar_pedido(entities)
            conversation_state = {}
        elif top_intent == "PreguntasFrecuentes":
            bot_response = handle_preguntas_frecuentes(entities)
            conversation_state = {}
        else:
            bot_response = "No entendí tu solicitud. ¿Puedes intentar de otra forma?"
            conversation_state = {}

    return jsonify({"reply": bot_response})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
