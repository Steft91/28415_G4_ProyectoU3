from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from src.controllers.auth import auth
from src.controllers.inversiones import inversiones
from src.models.database import get_db_connection, get_cuentas_usuario, obtener_inversiones_activas # <--- Importaciones Nuevas
from src.models.entities import User

app = Flask(__name__)
app.secret_key = 'pichincha_secret_key'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_usuario, username FROM usuarios WHERE id_usuario = %s", (user_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    if data:
        return User(data[0], data[1])
    return None

# Registro de Blueprints
app.register_blueprint(auth)
app.register_blueprint(inversiones, url_prefix='/inversiones')

# --- RUTA DASHBOARD MODIFICADA ---
@app.route('/dashboard')
@login_required 
def dashboard():
    # 1. Obtener Cuentas (Para mostrar saldo real en la parte superior)
    cuentas = get_cuentas_usuario(current_user.id)
    
    # 2. Obtener Inversiones Activas (Para el calendario simulador)
    inversiones_activas = obtener_inversiones_activas(current_user.id)
    
    return render_template('dashboard.html', 
                           cuentas=cuentas, 
                           inversiones=inversiones_activas)
# ---------------------------------

if __name__ == '__main__':
    app.run(debug=True)