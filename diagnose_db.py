import os
import sys

import pyodbc

# Cargar variables de entorno desde archivo .env
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("Variables de entorno cargadas desde .env")
except ImportError:
    print(
        "Advertencia: python-dotenv no está instalado. Usando variables de entorno del sistema."
    )
    pass

# --- 1. CONFIGURACIÓN CRÍTICA (cargada desde variables de entorno) ---
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DRIVER = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")

# Verificación de que las variables se cargaron
if not all([DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD]):
    print(
        "\n❌ ERROR CRÍTICO: Una o más variables de entorno de la base de datos no están definidas."
    )
    print(
        "Asegúrate de que tu archivo .env contenga DB_SERVER, DB_DATABASE, DB_USERNAME y DB_PASSWORD."
    )
    sys.exit(1)


def test_db_connection():
    print("--- Intentando conectar a Azure SQL Server ---")

    connection_string = (
        f"DRIVER={DRIVER};"
        f"SERVER={DB_SERVER},1433;"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no"
    )

    conn = None
    try:
        # Intenta la conexión
        conn = pyodbc.connect(connection_string)
        print("✅ CONEXIÓN EXITOSA: El usuario app_user funciona.")

        # Ejecuta una consulta simple de prueba
        cursor = conn.cursor()
        cursor.execute("SELECT GETDATE() AS ServerTime, SUSER_SNAME() AS CurrentUser;")
        row = cursor.fetchone()

        print("\n--- Resultados de la Consulta ---")
        print(f"Hora del Servidor: {row.ServerTime}")
        print(f"Usuario Conectado: {row.CurrentUser}")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print("\n❌ FALLO DE CONEXIÓN")
        print(f"Estado SQL: {sqlstate}")
        print(f"Mensaje de Error Completo: {ex}")

        if "28000" in sqlstate:
            print(
                "\nDIAGNÓSTICO: El error 28000 (Login failed) persiste. La contraseña aún es incorrecta."
            )
        elif "Driver not found" in str(ex):
            print("\nDIAGNÓSTICO: Error de driver. Revisa la variable 'DRIVER'.")

    finally:
        if conn:
            conn.close()
            print("Conexión cerrada.")


if __name__ == "__main__":
    test_db_connection()
