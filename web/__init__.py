## INICIALIZAR FLASK

from flask import Flask

# Definir la función de creación de la aplicación Flask
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'TrAbAjO*Tfe.UniR_2025'

    # Definir los ficheros de rutas que se van a usar
    from .views import views
    from .auth import auth

    # Registrar las rutas en la aplicación Flask, La raiz "/" sin prefijo para acceder a las rutas directamente por su nombre
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

