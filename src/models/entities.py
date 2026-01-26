from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_usuario, username, nombre_completo=None, cedula=None):
        self.id = str(id_usuario)  # Flask-Login requiere que el ID sea un string
        self.username = username
        self.nombre_completo = nombre_completo
        self.cedula = cedula

    @staticmethod
    def get_by_id(db_connection, user_id):
        """
        Busca un usuario por su ID. Útil para el user_loader de Flask-Login.
        """
        try:
            cur = db_connection.cursor()
            cur.execute("""
                SELECT id_usuario, username, nombre_completo, cedula 
                FROM usuarios WHERE id_usuario = %s
            """, (user_id,))
            data = cur.fetchone()
            cur.close()
            
            if data:
                return User(data[0], data[1], data[2], data[3])
            return None
        except Exception as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None