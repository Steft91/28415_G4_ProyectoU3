# src/models/database.py
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, date
from datetime import datetime, date, timedelta
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"\n⚠️  ERROR REAL DE BASE DE DATOS: {e}\n")
        return None

# --- FUNCIONES DE LECTURA ---

def get_cuentas_usuario(id_usuario):
    """Obtiene las cuentas de ahorro y corriente del usuario"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT tipo_origen, numero_cuenta, saldo_actual, id_interno FROM V_INV_CUENTAS_CLIENTE WHERE id_cliente = %s", (id_usuario,))
    cuentas = cur.fetchall()
    cur.close()
    conn.close()
    return cuentas

def get_producto_info(codigo_producto):
    """Obtiene tasa, monto min y plazo min de un producto"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT tasa_anual, monto_min, plazo_min_dias FROM INV_PRODUCTO WHERE codigo = %s", (codigo_producto,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    if data:
        return {'tasa': float(data[0]), 'monto_min': float(data[1]), 'plazo_min': int(data[2])}
    return None

def obtener_inversiones_activas(id_usuario):
    """Obtiene las inversiones que aun no han sido pagadas"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id_inversion, i.monto_capital, i.interes_ganado, i.total_a_recibir, 
               i.fecha_fin, i.id_cuenta_origen, p.nombre, i.fecha_inicio
        FROM INV_SOLICITUD i
        JOIN INV_PRODUCTO p ON i.id_producto = p.id_producto
        WHERE i.id_cliente = %s AND i.estado = 'ACTIVA'
        ORDER BY i.fecha_inicio DESC
    """, (id_usuario,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

# --- FUNCIONES TRANSACCIONALES (AQUÍ ESTABA EL ERROR) ---

def procesar_inversion(id_usuario, id_cuenta, monto, dias, tasa):
    """
    Realiza la transacción bancaria completa.
    Calcula la fecha en Python para evitar errores de sintaxis SQL.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Verificar saldo actual y tipo de cuenta
        cur.execute("""
            SELECT saldo_actual, 'AHORRO' as tipo FROM CUENTA_AHORROS WHERE id_cuenta = %s AND id_usuario = %s
            UNION
            SELECT saldo_actual, 'CORRIENTE' as tipo FROM CUENTA_CORRIENTE WHERE id_cuenta = %s AND id_usuario = %s
        """, (id_cuenta, id_usuario, id_cuenta, id_usuario))
        
        resultado = cur.fetchone()
        
        if not resultado:
            raise Exception("Cuenta no encontrada o no pertenece al usuario")
            
        saldo_actual, tipo_cuenta = resultado
        monto = float(monto)
        dias = int(dias) # Aseguramos que sea entero
        
        if saldo_actual < monto:
            raise Exception("Saldo insuficiente")

        # 2. Debitar el dinero (UPDATE)
        tabla_cuenta = "CUENTA_AHORROS" if tipo_cuenta == 'AHORRO' else "CUENTA_CORRIENTE"
        query_update = f"UPDATE {tabla_cuenta} SET saldo_actual = saldo_actual - %s WHERE id_cuenta = %s"
        cur.execute(query_update, (monto, id_cuenta))

        # 3. Calcular fechas y totales (EN PYTHON, NO EN SQL)
        fecha_actual = date.today()
        fecha_fin = fecha_actual + timedelta(days=dias) # Sumamos los días aquí
        
        interes_ganado = monto * (tasa / 100) * (float(dias) / 360)
        total_recibir = monto + interes_ganado

        # 4. Crear la Inversión (INSERT)
        # Pasamos fecha_fin directamente como parámetro
        cur.execute("""
            INSERT INTO INV_SOLICITUD 
            (id_cliente, id_producto, origen_fondos, id_cuenta_origen, monto_capital, fecha_inicio, fecha_fin, interes_ganado, total_a_recibir, estado)
            VALUES (%s, 1, %s, %s, %s, %s, %s, %s, %s, 'ACTIVA')
            RETURNING id_inversion
        """, (id_usuario, tipo_cuenta, id_cuenta, monto, fecha_actual, fecha_fin, interes_ganado, total_recibir))
        
        id_inversion_nueva = cur.fetchone()[0]

        # 5. Registrar el Movimiento (INSERT)
        cur.execute("""
            INSERT INTO INV_MOVIMIENTO_FINANCIERO (id_inversion, tipo_mov, monto, descripcion)
            VALUES (%s, 'DEBITO_APERTURA', %s, 'Débito por apertura de PlazoDólar')
        """, (id_inversion_nueva, monto))

        conn.commit()
        return True, "Inversión creada exitosamente"

    except Exception as e:
        conn.rollback()
        # Imprimir error en consola para debugging si es necesario
        print(f"ERROR DB: {e}") 
        return False, str(e)
    
    finally:
        cur.close()
        conn.close()

def simular_paso_tiempo(id_inversion, fecha_simulada):
    """
    Verifica si la fecha simulada supera la fecha de fin.
    Si es así, devuelve el dinero a la cuenta y marca la inversión como FINALIZADA.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT total_a_recibir, fecha_fin, id_cuenta_origen, estado FROM INV_SOLICITUD WHERE id_inversion = %s", (id_inversion,))
        inversion = cur.fetchone()
        
        if not inversion:
            return False, "Inversión no encontrada"
            
        total_pagar, fecha_fin, id_cuenta, estado = inversion
        
        if isinstance(fecha_simulada, str):
            fecha_simulada = datetime.strptime(fecha_simulada, '%Y-%m-%d').date()

        if estado == 'FINALIZADA':
            return False, "Esta inversión ya fue cobrada previamente."

        if fecha_simulada >= fecha_fin:
            cur.execute("SELECT 1 FROM CUENTA_AHORROS WHERE id_cuenta = %s", (id_cuenta,))
            es_ahorro = cur.fetchone()
            tabla = "CUENTA_AHORROS" if es_ahorro else "CUENTA_CORRIENTE"
            
            query_update = f"UPDATE {tabla} SET saldo_actual = saldo_actual + %s WHERE id_cuenta = %s"
            cur.execute(query_update, (total_pagar, id_cuenta))
            
            cur.execute("UPDATE INV_SOLICITUD SET estado = 'FINALIZADA' WHERE id_inversion = %s", (id_inversion,))
            
            cur.execute("""
                INSERT INTO INV_MOVIMIENTO_FINANCIERO (id_inversion, tipo_mov, monto, descripcion)
                VALUES (%s, 'CREDITO_VENCIMIENTO', %s, 'Acreditación por vencimiento de PlazoDolar')
            """, (id_inversion, total_pagar))
            
            conn.commit()
            return True, f"¡Fecha alcanzada! Se acreditaron ${total_pagar} a tu cuenta."
        
        else:
            dias_faltantes = (fecha_fin - fecha_simulada).days
            return False, f"Aún no vence ({fecha_fin}). Faltan {dias_faltantes} días."

    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()