## FICHERO "PLANTILLA" CON VISTAS/RUTAS GENERALES

from flask import Blueprint, render_template

# Variable que indica que este fichero plantilla con las vistas/rutas es 'views'
views = Blueprint('views', __name__)

# Ruta raiz
@views.route('/')
def index():
    return "Hello, World!"