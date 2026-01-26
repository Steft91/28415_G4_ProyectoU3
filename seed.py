# seed.py
from werkzeug.security import generate_password_hash
from src.models.database import get_db_connection

def crear_usuario_prueba():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Generamos el hash para 'pichincha123'
    password_encriptada = generate_password_hash('pichincha123')
    
    try:
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, cedula, nombre_completo)
            VALUES (%s, %s, %s, %s)
        """, ('stefy_admin', password_encriptada, '1712345678', 'Stefy Admin'))
        conn.commit()
        print("Usuario creado con éxito. Ahora puedes loguearte.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    crear_usuario_prueba()