from flask import Blueprint, render_template
from flask_login import login_required, current_user

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
    return render_template('inversiones/plazodolar.html')

@inversiones.route('/armadolar')
@login_required
def armadolar():
    return render_template('inversiones/armadolar.html')