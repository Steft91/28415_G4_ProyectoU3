from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.models.database import get_db_connection

inversiones = Blueprint('inversiones', __name__)

@inversiones.route('/dashboard')
@login_required
def dashboard():
    # Aquí podrías consultar el saldo del usuario usando la vista que creamos
    # conn = get_db_connection()
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM V_INV_CUENTAS_CLIENTE WHERE ID_CLIENTE = %s", (current_user.id,))
    # cuentas = cur.fetchall()
    
    return render_template('dashboard.html')

@inversiones.route('/plazodolar')
@login_required
def plazodolar():
    # Obtenemos la configuración del producto desde la BD
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT tasa_anual, monto_min, plazo_min_dias 
        FROM inv_producto 
        WHERE codigo = 'PLAZODOLAR'
    """)
    producto = cur.fetchone()
    cur.close()
    conn.close()

    # Pasamos los datos a la vista (si no existe, valores por defecto)
    tasa = producto[0] if producto else 6.50
    minimo = producto[1] if producto else 500.00
    plazo_min = producto[2] if producto else 30

    return render_template('inversiones/plazodolar.html', tasa=tasa, monto_min=minimo, plazo_min=plazo_min)

@inversiones.route('/armadolar')
@login_required
def armadolar():
    return render_template('inversiones/armadolar.html')