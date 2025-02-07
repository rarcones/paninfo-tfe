## ARRANQUE DE FLASK

# Importar el paquete y la función de la aplicación Flask que ha sido creado en web/ (Usa el fichero__init__.py).
from web import create_app

# Llamar a la función de creación para crear la instancia "app"
app = create_app()

# Ejecución de servidor Flask solo arrancando desde este fichero main, se evita que arranque si se importa en otro programa
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') # Arranca el servidor web de Flask con el puerto 5000 por defecto. Con modo debug activo para logging y reinicio cuando hay cambios