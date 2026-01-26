from flask import Flask, render_template
from flask_login import LoginManager, login_required
from src.controllers.auth import auth
from src.models.database import get_db_connection
from src.models.entities import User



app = Flask(__name__)
# En src/app.py
@app.route('/dashboard')
@login_required # Esto asegura que nadie entre sin loguearse
def dashboard():
    return render_template('dashboard.html')  

  
app.secret_key = 'pichincha_secret_key' # Cambia esto por algo más seguro

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
# app.register_blueprint(inversiones_bp) # Registra el de inversiones cuando lo tengas


if __name__ == '__main__':
    app.run(debug=True)