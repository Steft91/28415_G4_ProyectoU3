"""
Script para crear la base de datos y ejecutar el schema automáticamente
Ejecutar con: python crear_base_datos.py
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def crear_base_datos():
    # Primero conectarse a la base postgres por defecto
    print("📡 Conectando a PostgreSQL...")
    
    try:
        # Conexión a la base 'postgres' por defecto para crear nuestra DB
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',  # Base por defecto
            user='postgres',
            password='admin',  # ⚠️ CAMBIA ESTO por tu contraseña de PostgreSQL
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Verificar si la base ya existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'banco_pichincha'")
        existe = cur.fetchone()
        
        if existe:
            print("⚠️  La base de datos 'banco_pichincha' ya existe")
            respuesta = input("¿Deseas eliminarla y recrearla? (s/n): ")
            if respuesta.lower() == 's':
                # Cerrar conexiones activas
                cur.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = 'banco_pichincha'
                    AND pid <> pg_backend_pid()
                """)
                cur.execute("DROP DATABASE banco_pichincha")
                print("🗑️  Base de datos eliminada")
            else:
                print("❌ Operación cancelada")
                cur.close()
                conn.close()
                return False
        
        # Crear la base de datos
        cur.execute("CREATE DATABASE banco_pichincha")
        print("✅ Base de datos 'banco_pichincha' creada exitosamente")
        
        cur.close()
        conn.close()
        
        # Ahora conectarse a la nueva base para ejecutar el schema
        print("\n📄 Ejecutando el script SQL...")
        conn = psycopg2.connect(
            host='localhost',
            database='banco_pichincha',
            user='postgres',
            password='admin',  # ⚠️ CAMBIA ESTO por tu contraseña de PostgreSQL
            port=5432
        )
        cur = conn.cursor()
        
        # Leer y ejecutar el archivo SQL
        sql_path = os.path.join(os.path.dirname(__file__), 'database', '02_modulo_inversiones.sql')
        
        if not os.path.exists(sql_path):
            print(f"❌ No se encontró el archivo: {sql_path}")
            return False
            
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        cur.execute(sql_script)
        conn.commit()
        
        print("✅ Script SQL ejecutado exitosamente")
        print("\n" + "="*50)
        print("🎉 BASE DE DATOS LISTA PARA USAR")
        print("="*50)
        print("\n📋 Próximos pasos:")
        print("1. Crea el archivo .env en la raíz del proyecto")
        print("2. Ejecuta: python -m src.new (para crear usuario de prueba)")
        print("3. Ejecuta: python -m src.app (para iniciar la aplicación)")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica:")
        print("   - PostgreSQL está corriendo")
        print("   - La contraseña en este script es correcta (línea 17 y 44)")
        print("   - El puerto 5432 está disponible")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏦 BANCO PICHINCHA - Setup de Base de Datos")
    print("="*50)
    crear_base_datos()
