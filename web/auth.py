## FICHERO "PLANTILLA" CON VISTAS/RUTAS RELATIVAS A LA AUTENTICACIÓN

# Librerías para gestion de flask y usuarios/contraseñas
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash # Funciones de seguridad de contraseñas
from .models import Usuario # Clase Usuario (la tabla) del modulo models para operaciones con el listado de usuarios
from . import db # Importar el objeto db

auth = Blueprint('auth', __name__)

# Rutas
@auth.route('/login', methods=['GET','POST']) # Metodos que esta ruta acepta
def login(): # Mismo nombre dela función que el archivo
    if request.method == 'POST': # Obtener los datos recibidos del formulario
        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.query.filter_by(usuario=username).first() # Buscar el usuario en la base de datos. First solo devuelve la primera ocurrencia
        if user:
            if check_password_hash(user.password, password): # Comprobar que la contraseña es correcta
                flash('Inicio de sesion correcto', category='OK')
                login_user(user, remember=True) # Recuerda la sesion hasta hacer logout, borrar cookies o reiniciar el servidor
                return redirect(url_for('views.home')) # Redireccion al logarse a la página home (Funcion /home de views.py)
            else:
                flash('Contraseña incorrecta', category='NOK') # Visualización de mensaje, en este caso de error NOK, por la funcionalidad flash de flask, definida en el layout.html
        else:
            flash('No existe el usuario', category='NOK')

    return render_template("login.html", user=current_user) # Renderizar de nuevo la página login.html para que se autentique
    
@auth.route('/useradd', methods=['GET','POST']) # Decorador de la ruta de la pagina de registro de usuario
@login_required
def useradd():
    if request.method == 'POST':  
        username = request.form.get('username')
        password = request.form.get('password')
        passwordCheck = request.form.get('passwordCheck')
        
        # Comprobación que el usuario no exista
        user = Usuario.query.filter_by(usuario=username).first()
        if user:
            flash('El usuario ya existe', category='NOK')
        # Validacion de datos a ingresar básica
        elif len(username) < 4:
            flash('El usuario debe tener al menos 4 caracteres.', category='NOK')
        elif len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', category='NOK')
        elif password != passwordCheck:
            flash('Las contraseñas no coinciden.', category='NOK')
        else:
            # Escribir en la BBDD la creacion del nuevo usuario
            new_user = Usuario(usuario=username, password=generate_password_hash(password)) # Crear un nuevo usuario con los datos del formulario. method='pbkdf2:sha256'
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario nuevo creado', category='OK')
            #login_user(user, remember=True) # Aprovecha el nuevo usuario y recuerda la sesion hasta hacer logout
            return redirect(url_for('views.home')) # Redireccion a la homepage (Funcion home en views.py). Usar ('Blueprint.funcion') es mejor que usar la ruta / directamente

    # Listado de usuarios para mostrar, excluyendo el creado con el script de instalacion
    usuarios = Usuario.query.filter(Usuario.id > 1).all()
    
    return render_template("useradd.html", user=current_user, list_users=usuarios)
        

@auth.route('/logout')
@login_required
def logout():
    logout_user()   # Cerrar la sesion del usuario actual
    return redirect(url_for('views.index')) # Redireccion a la pagina de login (ruta auth, funcion login)
