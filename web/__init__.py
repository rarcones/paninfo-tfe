## FICHERO PRINCIPAL DE DEFINICION DE LA APLICACION WEB FLASK

# Librerías propias de Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy # Clase SQLAlchemy de Flask-SQLAlchemy para el uso de la BD
from flask_login import LoginManager # Clase LoginManager de Flask-Login para gestionar el login
# Librerías para ejecutar acciones en el SO (path para la creacion de la BD en la ruta de la app)
from os import path
import os

# Definicion de la base de datos
db = SQLAlchemy() # Crear un objeto SQLAlchemy para la base de datos
DB_NAME = "paninfo.db" # Variable con el nombre de la base de datos

# Función de creación de la aplicación Flask
def create_app():
    
    # Aplicacion Flask con la ruta relativa del modulo actual (__name__)
    app = Flask(__name__) # Crear un objeto Flask "app"
    app.config['SECRET_KEY'] = 'TrAbAjO*Tfe.UniR_2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.root_path, DB_NAME)}' # SQLAlchemy usara una base de datos sqlite, situada en el directorio de la app (web), con el nombre que se le ha dado en la variable DB_NAME. "///" significa ruta relativa
    db.init_app(app) # Inicializar la base de datos para la app

    # Definir los ficheros de rutas con las páginas de la que se compone la aplicación web
    from .views import views # .views indica que es el fichero views.py en el directorio actual, y views es el blueprint de las rutas que estan en el fichero
    from .auth import auth

    # Registrar las rutas en Flask, indicando los ficheros. La raiz "/" indica sin prefijo añadido para acceder a las rutas directamente por el nombre del blueprint correspondiente
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Importar los modelos de la base de datos y crear la BD
    from .models import Usuario #, Incidente, Tipoincidente, Mensajeold # Importar las clases de los modelos/tablas de la base de datos
    create_db(app) # llamada a la funcion create_db con nuestro nombre de app (app)

    # Configuración de Login Manager, una vez importada la clase Usuario, para poder usar la funcion load_user
    login_manager = LoginManager() # Crear un objeto LoginManager
    login_manager.login_view = 'auth.login' # Definir la ruta por defecto que se mostrará al usuario no logeado (ruta de login)
    login_manager.init_app(app) # Especificar a LoginManager su uso en la aplicacion Flask del panel informativo (app)
    
    # Decorador para cargar el usuario en Flask
    @login_manager.user_loader 
    def load_user(id): # Funcion para cargar el usuario usando el ID de la table en la BD
        return Usuario.query.get(int(id)) # Devolver el usuario con el id pasado como parametro, convertido a entero. Se asigna a la variable interna "current_user" de la librería

    # Subida de contenido, definiendo el directorio que hace de repositorio y creándolo si no existe.  
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/media')
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app

# Función de creacion de la BD
def create_db(app):
    if not path.exists('web/' + DB_NAME): # Si la base de datos no existe, se crea
        with app.app_context():
            db.create_all()
            print("Base de datos de la aplicación creada") # Mostrar mensaje de que la base de datos ha sido creada
