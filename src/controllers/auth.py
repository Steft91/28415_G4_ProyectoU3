# src/controllers/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from src.models.database import get_db_connection
from src.models.entities import User

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            flash("Error de conexión a la base de datos")
            return render_template('login.html')

        cur = conn.cursor()
        # Buscamos al usuario por su username
        cur.execute("SELECT id_usuario, username, password_hash FROM usuarios WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if user_data and check_password_hash(user_data[2], password):
            # Si la contraseña coincide, creamos el objeto User y logueamos
            user_obj = User(user_data[0], user_data[1])
            login_user(user_obj)
            # ¡Aquí es donde ocurre el salto a la siguiente ventana!
            return redirect(url_for('dashboard')) 
        else:
            flash("Credenciales inválidas")
            
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user() # Esto borra la sesión del usuario
    return redirect(url_for('auth.login')) # Te devuelve a la pantalla de login