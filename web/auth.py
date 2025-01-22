## FICHERO "PLANTILLA" CON VISTAS/RUTAS RELATIVAS A LA AUTENTICACIÓN

from flask import Blueprint

# Variable que indica que este fichero plantilla con las vistas/rutas es 'views'
auth = Blueprint('auth', __name__)

# Ruta de login con su función
@auth.route('/login')
def login():
    return "Login"

# Ruta de creación de usuario con su función
@auth.route('/useradd')
def useradd():
    return "Nuevo usuario"

# Ruta de creación de logout con su función
@auth.route('/logout')
def logout():
    return "Cerrar sesión"