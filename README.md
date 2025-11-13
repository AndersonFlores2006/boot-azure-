# BotEcomerce: Chatbot de E-commerce con Azure CLU y Flask

Este proyecto implementa un chatbot de e-commerce utilizando Flask para el backend, Azure Language Understanding (CLU) para el procesamiento del lenguaje natural, y una base de datos SQL para la gestión de pedidos y preguntas frecuentes.

## Características

- **Creación de Pedidos:** Permite a los usuarios crear nuevos pedidos especificando productos, cantidades y métodos de pago.
- **Consulta de Pedidos:** Los usuarios pueden consultar el estado de sus pedidos existentes.
- **Pago de Pedidos:** Funcionalidad para marcar pedidos como pagados.
- **Preguntas Frecuentes:** Responde a preguntas comunes sobre horarios, envíos, devoluciones, etc.
- **Integración con Azure CLU:** Utiliza un modelo de lenguaje conversacional para entender las intenciones y entidades del usuario.
- **Persistencia de Datos:** Conexión a una base de datos SQL para almacenar y recuperar información.

## Prerrequisitos

Antes de empezar, asegúrate de tener instalado lo siguiente:

- **Python 3.8+**
- **pip** (gestor de paquetes de Python)
- Una cuenta de **Azure**
    - Un recurso de **Azure Cognitive Services** (con la capacidad de Language Understanding).
    - Una **Azure SQL Database**.

## Configuración del Proyecto

Sigue estos pasos para configurar y ejecutar el proyecto localmente:

### 1. Clonar el Repositorio

```bash
git clone https://github.com/AndersonFlores2006/boot-azure-.git
cd BotEcomerce
```

### 2. Crear y Activar un Entorno Virtual

Es una buena práctica trabajar con entornos virtuales para gestionar las dependencias del proyecto.

```bash
python -m venv venv
# En Linux/macOS:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate
```

### 3. Instalar Dependencias

Instala todas las librerías necesarias utilizando `pip`:

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo llamado `.env` en el directorio `BotEcomerce`. Este archivo contendrá tus secretos y configuraciones que no deben ser versionadas en Git.

**Ejemplo de `.env`:**

```
COGNITIVE_SERVICES_KEY="TU_CLAVE_DE_AZURE_COGNITIVE_SERVICES"
ENDPOINT_URL="https://TU_ENDPOINT_DE_AZURE_CLU.cognitiveservices.azure.com/language/:analyze-conversations?api-version=2024-11-15-preview"
PROJECT_NAME="nombre-de-tu-proyecto-clu" # Ejemplo: chatbot-final
DEPLOYMENT_NAME="nombre-de-tu-despliegue-clu" # Ejemplo: ChatbotEcomerce

DB_SERVER="tcp:TU_SERVIDOR_SQL.database.windows.net,1433"
DB_DATABASE="TU_NOMBRE_DE_BASE_DE_DATOS_SQL"
DB_USERNAME="TU_USUARIO_SQL"
DB_PASSWORD="TU_CONTRASEÑA_SQL"

DEBUG_DB="true" # Establece a 'true' para ver mensajes de depuración de la DB, 'false' para deshabilitar.
```

Asegúrate de reemplazar los valores con `TU_...` por tus credenciales y nombres de recursos reales de Azure.
El archivo `.env` ya está incluido en `.gitignore`, por lo que no se subirá al repositorio.

### 5. Configuración de la Base de Datos SQL

Asegúrate de que tu Azure SQL Database esté configurada y contenga las tablas `Pedidos` y `PreguntasFrecuentes` con las estructuras adecuadas para el funcionamiento del bot. El script `diagnose_db.py` puede ayudarte a verificar la conectividad.

### 6. Ejecutar la Aplicación

Una vez que todas las dependencias y variables de entorno estén configuradas, puedes iniciar la aplicación Flask:

```bash
python botEcomerce.py
```

El chatbot estará disponible en `http://127.0.0.1:5000`.

## Despliegue en Azure App Service

Para desplegar esta aplicación en Azure App Service, sigue estos pasos:

### 1. Preparar Recursos de Azure

Asegúrate de tener un Azure App Service creado, junto con tu recurso de Azure Cognitive Services y Azure SQL Database.

### 2. Configurar Variables de Entorno en App Service

En el portal de Azure, ve a tu App Service, luego a "Configuración" -> "Variables de entorno" y añade las mismas variables que configuraste en tu archivo `.env`:

- `COGNITIVE_SERVICES_KEY`
- `ENDPOINT_URL`
- `PROJECT_NAME`
- `DEPLOYMENT_NAME`
- `DB_SERVER`
- `DB_DATABASE`
- `DB_USERNAME`
- `DB_PASSWORD`
- `DEBUG_DB`

Alternativamente, puedes usar la Azure CLI:

```bash
az webapp config appsettings set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --settings \
    COGNITIVE_SERVICES_KEY="TU_CLAVE_DE_AZURE_COGNITIVE_SERVICES" \
    ENDPOINT_URL="https://TU_ENDPOINT_DE_AZURE_CLU.cognitiveservices.azure.com/language/:analyze-conversations?api-version=2024-11-15-preview" \
    PROJECT_NAME="nombre-de-tu-proyecto-clu" \
    DEPLOYMENT_NAME="nombre-de-tu-despliegue-clu" \
    DB_SERVER="tcp:TU_SERVIDOR_SQL.database.windows.net,1433" \
    DB_DATABASE="TU_NOMBRE_DE_BASE_DE_DATOS_SQL" \
    DB_USERNAME="TU_USUARIO_SQL" \
    DB_PASSWORD="TU_CONTRASEÑA_SQL" \
    DEBUG_DB="false"
```
Recuerda reemplazar los placeholders con tus valores reales.

### 3. Usar el Script de Despliegue (Opcional)

El script `despliegue.sh` puede automatizar algunos pasos del despliegue. Revisa su contenido y adáptalo a tu configuración si es necesario.

## Estructura del Proyecto

- `BotEcomerce/`: Directorio principal de la aplicación
    - `static/`: Contiene archivos estáticos como CSS, JavaScript e imágenes.
    - `templates/`: Contiene las plantillas HTML (Jinja2) para la interfaz de usuario.
    - `venv/`: Entorno virtual de Python (ignorado por Git).
    - `AZURE_DEPLOYMENT_GUIDE.md`: Guía detallada para el despliegue en Azure (posiblemente).
    - `README.md`: Este archivo de información del proyecto.
    - `botEcomerce.py`: La lógica principal de la aplicación Flask y el chatbot.
    - `clu_project.json`: Definición del proyecto de Language Understanding (CLU).
    - `despliegue.sh`: Script para automatizar tareas de despliegue.
    - `diagnose_db.py`: Script para diagnosticar la conexión a la base de datos.
    - `requirements.txt`: Lista de dependencias de Python.

## Uso del Chatbot

Accede a la aplicación web (localmente o en Azure) y comienza a interactuar con el chatbot. Puedes probar comandos como:

- "Quiero crear un pedido de 2 camisetas con tarjeta"
- "Cuál es el estado de mi pedido 12345"
- "Quiero pagar el pedido 67890"
- "¿Cuál es el horario de atención?"

## Contribución

Si deseas contribuir a este proyecto, por favor, haz un fork del repositorio y envía tus pull requests.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

#despliegue
  git add .
  git commit -m "Actualizado el subtítulo del encabezado"
  git push azure main:master --force
