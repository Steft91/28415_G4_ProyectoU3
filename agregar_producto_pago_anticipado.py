"""
Script para agregar el producto PAGOANTICIPADO a la base de datos
Ejecutar con: python agregar_producto_pago_anticipado.py
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def agregar_producto():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        
        # Verificar si ya existe
        cur.execute("SELECT 1 FROM INV_PRODUCTO WHERE CODIGO = 'PAGOANTICIPADO'")
        if cur.fetchone():
            print("⚠️  El producto PAGOANTICIPADO ya existe en la base de datos")
            cur.close()
            conn.close()
            return
        
        # Insertar el producto
        cur.execute("""
            INSERT INTO INV_PRODUCTO (CODIGO, NOMBRE, TASA_ANUAL, MONTO_MIN, PLAZO_MIN_DIAS, ES_FLEXIBLE) 
            VALUES ('PAGOANTICIPADO', 'Inversión con Pago Anticipado', 6.00, 500.00, 30, FALSE)
        """)
        
        conn.commit()
        
        print("=" * 60)
        print("✅ PRODUCTO AGREGADO EXITOSAMENTE")
        print("=" * 60)
        print("\n📋 Detalles del producto:")
        print("   • Código: PAGOANTICIPADO")
        print("   • Nombre: Inversión con Pago Anticipado")
        print("   • Tasa: 6.00% anual")
        print("   • Monto mínimo: $500")
        print("   • Plazo mínimo: 30 días")
        print("   • Plazo máximo: 179 días")
        print("\n✅ Ya puedes acceder a la funcionalidad desde:")
        print("   http://127.0.0.1:5000/inversiones/pago-anticipado")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🏦 Agregando producto PAGO ANTICIPADO\n")
    agregar_producto()
