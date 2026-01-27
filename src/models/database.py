# src/models/database.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv() # Esto carga el archivo .env

def get_db_connection():
    # --- AGREGA ESTAS LÍNEAS DE DIAGNÓSTICO ---
    nombre_db = os.getenv('DB_NAME')
    print(f"----------------------------------------")
    print(f"👀 INTENTANDO CONECTAR A LA BASE: '{nombre_db}'")
    print(f"----------------------------------------")
    # ------------------------------------------

    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=nombre_db, # Usa la variable aquí
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"\n⚠️  ERROR REAL DE BASE DE DATOS: {e}\n")
        return None