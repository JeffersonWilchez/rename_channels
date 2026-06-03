import os
import mysql.connector
from requests import get as requests_get, patch as requests_patch, post as requests_post
from dotenv import load_dotenv
from urllib3 import response

load_dotenv()

TABLA = "clases"
PERIODO = "periodo"
NOMBRE_CLASE = "titulo_teams"

def connection_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
        print("Conexión exitosa a la base de datos")
        return conn
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def get_clases():
    periodo_srt = input("Ingrese el periodo (Ejemplo: 2025-2026): \n")

    if not periodo_srt:
        print("El periodo es requerido")
        return

    conn = None
    cursor = None
    
    try:
        conn = connection_db()

        if not conn:
            return
        
        query = f"""SELECT DISTINCT {NOMBRE_CLASE} FROM {TABLA} WHERE {PERIODO} = %s AND {NOMBRE_CLASE} IS NOT NULL"""

        cursor = conn.cursor()
        cursor.execute(query, (periodo_srt,))
        clases = [clase[0] for clase in cursor.fetchall()]

        if not clases:
            print("No se encontraron clases para el periodo ingresado")
            return None
        
        print(f"Se encontraron {len(clases)} clases para el periodo {periodo_srt}")
        print(clases)
        return clases

    except mysql.connector.Error as e:
        print(f"Error al obtener las clases: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_token_teams():
    url = os.getenv("ACCESS_TOKEN_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests_post(url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error al obtener el token: {response.status_code}")
        return None

def get_id_tems(token, clase):
    url = f"https://graph.microsoft.com/v1.0/teams?filter=displayName eq '{clase}'"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests_get(url, headers=headers)
    if response.status_code == 200:
        print(f"ID de la clase: {response.json()['value'][0]['id']}")
        return response.json()["value"][0]["id"]
    else:
        print(f"Error al obtener el id de la clase: {response.status_code} - {response.json()['error']['message']}")
        return None

if __name__ == "__main__":
    token = get_token_teams()
    if token:
        clases = get_clases()
        if clases:
            for clase in clases:
                get_id_tems(token, clase)
