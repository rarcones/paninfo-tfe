##ARRANQUE DE FLASK

# Importar el paquete de la aplicación Flask creada en web/. Usa el fichero__init__
from web import create_app

# Llamar a la función de creación/arranque
app = create_app()

# Ejecución de servidor Flask solo arrancando desde el fichero main, se evita que arranque si se importa en otro programa
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') # Puerto 5000 por defecto. Modo debug para logging y reinicio cuando hay cambios