## INICIALIZAR FLASK

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager # Clase LoginManager de Flask-Login para gestionar el login
# Librerías para el so (path para la creacion de la BD en la ruta de la app)
from os import path
import os


# Definicion de la base de datos
db = SQLAlchemy() # Crear un objeto SQLAlchemy para la base de datos
DB_NAME = "paninfo.db" # Nombre de la base de datos


# Definir la función de creación de la aplicación Flask
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'TrAbAjO*Tfe.UniR_2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.root_path, DB_NAME)}' # SQLAlchemy usara una base de datos sqlite, situada en el directorio de la app (web), con el nombre que se le ha dado en la variable DB_NAME. "///" significa ruta relativa
    db.init_app(app) # Inicializar la base de datos para la app

    # Definir los ficheros de rutas que se van a usar
    from .views import views
    from .auth import auth

    # Registrar las rutas en la aplicación Flask, La raiz "/" sin prefijo para acceder a las rutas directamente por su nombre
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Usuario #, Incidente, Tipoincidente, Mensajeold # Importar las clases de los modelos/tablas de la base de datos
    create_db(app) # llamada a la funcion create_db con nuestro nombre de app (app)

    # Login Manager, una vez importada la clase Usuario, para poder usar la funcion load_user
    login_manager = LoginManager() # Crear un objeto LoginManager
    login_manager.login_view = 'auth.login' # Definir la ruta por defecto al no estar logeado (ruta de login)
    login_manager.init_app(app) # Especificar a LoginManager su uso con la aplicacion Flask de nombre app
    
    @login_manager.user_loader # Decorador para cargar el usuario en Flask
    def load_user(id): # Funcion para cargar el usuario
        return Usuario.query.get(int(id)) # Devolver el usuario con el id pasado como parametro, convertido a entero. Usando directamente la PK que es id

    return app

# Función de creacion de la BD
def create_db(app):
    if not path.exists('web/' + DB_NAME): # Si la base de datos no existe, se crea
        with app.app_context():
            db.create_all()
            print("Base de datos de la aplicación creada") # Mostrar mensaje de que la base de datos ha sido creada
