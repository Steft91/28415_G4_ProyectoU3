# src/crear_test_user.py
from werkzeug.security import generate_password_hash
from src.models.database import get_db_connection

def crear_usuario_nuevo():
    conn = get_db_connection()
    if not conn:
        print("❌ Error: No se pudo conectar a la base de datos.")
        return

    cur = conn.cursor()
    # 1. Definimos las credenciales
    nuevo_usuario = 'user_test1'
    clave_plana = 'pichincha2026'
    
    # 2. Generamos el HASH (esto es lo que se guarda)
    password_encriptada = generate_password_hash(clave_plana)
    
    try:
        # 3. Insertamos el usuario y obtenemos su ID
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, cedula, nombre_completo)
            VALUES (%s, %s, %s, %s) RETURNING id_usuario
        """, (nuevo_usuario, password_encriptada, '1722582317', 'Usuario de Pruebas'))
        
        id_generado = cur.fetchone()[0]

        # 4. LE CREAMOS UNA CUENTA (Para que el Dashboard no falle)
        cur.execute("""
            INSERT INTO cuenta_ahorros (n_cuenta, id_usuario, saldo_actual)
            VALUES (%s, %s, %s)
        """, ('2200001123', id_generado, 5000.00))

        conn.commit() # 👈 SIN ESTO, LOS CAMBIOS NO SE GUARDAN EN POSTGRES
        
        print("-" * 30)
        print(f"✅ USUARIO CREADO CON ÉXITO")
        print(f"👤 Usuario: {nuevo_usuario}")
        print(f"🔑 Contraseña: {clave_plana}")
        print(f"💰 Saldo inicial: $5000.00")
        print("-" * 30)

    except Exception as e:
        conn.rollback()
        print(f"❌ Error al crear usuario: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    crear_usuario_nuevo()