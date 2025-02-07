## FICHERO "PLANTILLA" CON VISTAS/RUTAS GENERALES. USADO DESDE __init__.py

# Librerias para la web
from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response, current_app # Clase Blueprint de Flask y funciones de Flask
from flask_login import login_required, current_user # Flask-Login para el manejo de usuarios. Login_required como decorador para que solo se muestre la ruta una vez autenticado y Current_user para saber si el usuario esta logado, lee los atributos del modelo Usuario de la bd.
from datetime import datetime # datetime para el manejo de horas/fecha
# Librerias para el acceso a la base de datos
from .models import Usuario, Empresa, TipoLesion, CausaLesion, Accidente, Contenido, Mensaje, MensajePrioritario  # Importar las clases de las tablas a usar desde la librería models (Fichero models.py)
from . import db
# Librerías para exportar a csv
import csv  # Para leer y escribir csv
import io # Para manejo de ficheros
# Librerías para para subir contenido
from werkzeug.utils import secure_filename
import os

# Crear un objeto Blueprint llamado 'views' con el nombre del modulo actual (__name__), tal como se indica en la documentación de Flask
views = Blueprint('views', __name__) 

# Rutas (Páginas) de la aplicacion web
# Define la ruta base. Cuando el usuario accede a la raíz de la web "/", se llama a la función que muestra ella plantilla index.html, con el valor de la variable user del usuario autenticado.
@views.route('/')
def index():
    return render_template("index.html", user=current_user)

# Define la ruta de inicio al logarse el usuario
@views.route('/home', methods=['GET'])
@login_required
def home(): 
    now = datetime.now()
    #Contenido en emision actual en base a ciertas reglas, consultado a las tablas de la BD
    contenidos_act = Contenido.query.filter_by(programado=True).all()
    mensajes_act = Mensaje.query.all()
    mens_prioritarios_act = (MensajePrioritario.query.filter(MensajePrioritario.activo==True, MensajePrioritario.mp_visualizado==False, MensajePrioritario.fecha_desde <= now,  MensajePrioritario.fecha_hasta >= now).all()) #Filtros exactos para mostrar solo los prioritarios en ejecucion
    return render_template("home.html", user=current_user, contenidos_act=contenidos_act, mensajes_act=mensajes_act, mens_prioritarios_act=mens_prioritarios_act) # Renderizar el template homepage.html con el usuario logeado

# Define la ruta que muestra el listado de datos en las tres tablas auxiliares para el formulario de accidentes
@views.route('/gestdatos', methods=['GET'])
@login_required
def gestdatos():
    # Listado datos de las tres tablas
    list_empresas = Empresa.query.order_by(Empresa.nombre_empresa.asc()).all()
    list_tipoles = TipoLesion.query.order_by(TipoLesion.tipo.asc()).all()
    list_causales = CausaLesion.query.order_by(CausaLesion.causa.asc()).all()
    return render_template(
        "gestdatos.html",
        user=current_user,
        list_empresas=list_empresas,
        list_tipoles=list_tipoles,
        list_causales=list_causales
    )

# Define la ruta particular para añadir empresas
@views.route('/gestdatos/addemp', methods=['POST']) 
@login_required
def addemp():
    nombre_empresa = request.form.get('nombre_empresa')
    nif = request.form.get('nif')

    if not nombre_empresa or not nif:
        flash('Por favor, rellene nombre de empresa y NIF.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    emp_exist = Empresa.query.filter_by(nif=nif).first()
    if emp_exist:
        flash('Ya existe una empresa con ese NIF.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    new_emp = Empresa(nombre_empresa=nombre_empresa, nif=nif)
    db.session.add(new_emp)
    db.session.commit()
    flash('Empresa creada exitosamente.', category='OK')
    return redirect(url_for('views.gestdatos'))

# Define la ruta particular para editar las empresas
@views.route('/gestdatos/editemp/<int:empresa_id>', methods=['POST'])
@login_required
def editemp(empresa_id):
    nombre_empresa = request.form.get('nombre_empresa')
    nif = request.form.get('nif')

    if not nombre_empresa or not nif:
        flash('Todos los campos son obligatorios.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    empresa = Empresa.query.get(empresa_id)

    # Verificar si el NIF ya existe en otra empresa
    emp_exist = Empresa.query.filter(Empresa.nif == nif, Empresa.id != empresa_id).first()
    if emp_exist:
        flash('Ya existe una empresa con ese NIF.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    empresa.nombre_empresa = nombre_empresa
    empresa.nif = nif
    db.session.commit()
    flash('Empresa actualizada con éxito.', category='OK')
    return redirect(url_for('views.gestdatos'))

# Define la ruta particular para añadir tipos de lesiones
@views.route('/gestdatos/addtipo', methods=['POST'])
@login_required
def addtipo():
    tipo_lesion = request.form.get('tipo_lesion')

    if not tipo_lesion:
        flash('Por favor, rellene el tipo de lesión.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    new_tipoles = TipoLesion(tipo=tipo_lesion)
    db.session.add(new_tipoles)
    db.session.commit()
    flash('Tipo de lesión creado exitosamente.', category='OK')
    return redirect(url_for('views.gestdatos'))

# Define la ruta particular para borrar tipos de lesiones
@views.route('/gestdatos/deltipo/<int:tipolesion_id>', methods=['POST'])
@login_required
def deltipo(tipolesion_id):
    tipolesion = TipoLesion.query.get_or_404(tipolesion_id)

    db.session.delete(tipolesion)
    db.session.commit()
    flash('Tipo de lesión eliminado con éxito.', category='OK')
    return redirect(url_for('views.gestdatos'))

# Define la ruta particular para añadir causas de lesiones
@views.route('/gestdatos/addcausa', methods=['POST'])
@login_required
def addcausa():
    causa_lesion = request.form.get('causa_lesion')

    if not causa_lesion:
        flash('Por favor, rellene la causa de lesión.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    # Opcional: Verificar si la causa ya existe
    causa_exist = CausaLesion.query.filter_by(causa=causa_lesion).first()
    if causa_exist:
        flash('Ya existe una causa de lesión con ese nombre.', category='NOK')
        return redirect(url_for('views.gestdatos'))

    # Crear y guardar la nueva causa de lesión
    new_causales = CausaLesion(causa=causa_lesion)
    db.session.add(new_causales)
    db.session.commit()
    flash('Causa de lesión creada exitosamente.', category='OK')
    return redirect(url_for('views.gestdatos'))

# Define la ruta particular para borrar causas de lesiones
@views.route('/gestdatos/delcausa/<int:causalesion_id>', methods=['POST'])
@login_required
def delcausa(causalesion_id):
    causalesion = CausaLesion.query.get_or_404(causalesion_id)

    db.session.delete(causalesion)
    db.session.commit()
    flash('Causa de lesión eliminada con éxito.', category='OK')
    return redirect(url_for('views.gestdatos'))


# Define la ruta particular para mostrar el formulario de creación de accidentes
@views.route('/gestacc', methods=['GET', 'POST'])
@login_required 
def gestacc():

    # Formulario de creacion de accidente
    if request.method == 'POST':
        # id_usuario = request.form.get('id_usuario') No se necesita, ya que el usuario actual es el que crea el accidente
        # Tampoco fecha de registro, ya que se añade automáticamente en el modelo
        id_usuario = current_user.id # El id del usuario PRL que lo crea lo toma automáticamente del usuario logado
        id_empresa = request.form.get('id_empresa')
        id_causalesion = request.form.get('id_causalesion')
        id_tipolesion = request.form.get('id_tipolesion')
        nombre_trabajador = request.form.get('nombre_trabajador')
        es_baja = request.form.get('es_baja')  # Vendrá como 'on' si está marcado
        fecha_baja = request.form.get('fecha_baja')
        fecha_alta = request.form.get('fecha_alta')

        # 2. Procesar campos booleanos y de fecha/hora
        es_baja = True if es_baja == 'on' else False

        # Para datetime con hora, usar '%Y-%m-%dT%H:%M' y type="datetime-local" en el HTML
        fecha_baja = datetime.strptime(fecha_baja, '%Y-%m-%d') if fecha_baja else None
        fecha_alta = datetime.strptime(fecha_alta, '%Y-%m-%d') if fecha_alta else None       

        # 3. Crear el nuevo objeto Accidente
        new_accidente = Accidente(id_usuario=id_usuario, id_empresa=id_empresa, id_causalesion=id_causalesion, id_tipolesion=id_tipolesion, nombre_trabajador=nombre_trabajador, es_baja=es_baja, fecha_baja=fecha_baja, fecha_alta=fecha_alta)

        # 4. Guardarlo en la base de datos
        db.session.add(new_accidente)
        db.session.commit()
        flash('Accidente registrado con éxito', category='OK')

        return redirect(url_for('views.gestacc'))

    # Deplegables de las tablas relacionadas
    # list_usuarios = Usuario.query.all()  No se necesita, ya que el usuario actual es el que crea el accidente
    list_empresas = Empresa.query.all()
    list_causas = CausaLesion.query.all()
    list_tipos = TipoLesion.query.all()

    return render_template('gestacc.html', user=current_user, list_empresas=list_empresas, list_causas=list_causas, list_tipos=list_tipos)

# Define la ruta para mostrar el listado de accidentes
@views.route('/listacc', methods=['GET']) # Sólo GET para mostrar la información
@login_required 
def listacc():
    list_empresas = Empresa.query.all()
    list_causas   = CausaLesion.query.all()
    list_tipos    = TipoLesion.query.all()
    list_accidentes = Accidente.query.all()

    return render_template("listacc.html", list_empresas=list_empresas, list_causas=list_causas, list_tipos=list_tipos, list_accidentes=list_accidentes, user=current_user)

# Define la ruta particular para editar accidentes
@views.route('/listacc/editacc', methods=['POST'])
@login_required 
def editacc():
    acc_id = request.form.get('acc_id')  # ID del accidente a editar
    accidente = Accidente.query.get(acc_id)
    
    # Recoger datos del formulario
    id_empresa = request.form.get('id_empresa')
    id_causalesion   = request.form.get('id_causalesion')
    id_tipolesion    = request.form.get('id_tipolesion')
    nombre_trabajador = request.form.get('nombre_trabajador')
    es_baja = request.form.get('es_baja')  # 'on' si está marcado
    fecha_baja = request.form.get('fecha_baja')
    fecha_alta = request.form.get('fecha_alta')
    
    # Actualizar objeto
    accidente.id_empresa = id_empresa
    accidente.id_causalesion = id_causalesion
    accidente.id_tipolesion  = id_tipolesion
    accidente.nombre_trabajador = nombre_trabajador
    accidente.es_baja = True if es_baja == 'on' else False
    accidente.fecha_baja = datetime.strptime(fecha_baja, '%Y-%m-%d') if fecha_baja else None
    accidente.fecha_alta = datetime.strptime(fecha_alta, '%Y-%m-%d') if fecha_alta else None
    
    db.session.commit()
    flash("Accidente actualizado con éxito", category='OK')
    return redirect(url_for('views.listacc'))

# Define la ruta particular para exportar el listado de accidentes a csv
@views.route('/listacc/exportacc', methods=['GET'])
@login_required 
def exportacc():
    accidentes = Accidente.query.all()
    
    # Crear un objeto de tipo StringIO para escribir el CSV
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';') # Por defecto Excel no separa por comas correctamente, si añadimos que separe por ; si funciona. 

    # Escribir la cabecera del csv para identificar las columnas
    writer.writerow(['ID', 'FECHA REGISTRO', 'USUARIO PRL', 'EMPRESA', 'CAUSA', 'TIPO', 'NOMBRE TRABAJADOR', 'BAJA', 'FECHA BAJA', 'FECHA ALTA'])

    # Leer los datos de la tabla y escribirlos en el CSV
    for acc in accidentes:
        writer.writerow([ acc.id, acc.fecha_registro.strftime('%d/%m/%Y') if acc.fecha_registro else "", acc.usuario.usuario if acc.usuario else "", acc.empresa.nombre_empresa if acc.empresa else "", acc.causa_lesion.causa if acc.causa_lesion else "", acc.tipo_lesion.tipo if acc.tipo_lesion else "", acc.nombre_trabajador, acc.es_baja, acc.fecha_baja.strftime('%d/%m/%Y') if acc.fecha_baja else "", acc.fecha_alta.strftime('%d/%m/%Y') if acc.fecha_alta else ""])

    # Descarga mediante respuesta HTTP que hace que el navegador lo ejecute como un archivo adjunto para descargar
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=ListadoAccidentes.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response

# Define la ruta de la página de creación de contenido
@views.route('/mediaplayer', methods=['GET', 'POST'])
@login_required 
def mediaplayer():
    if request.method == 'POST':
        # Obtener datos del formulario
        archivo = request.files.get('archivo')
        numero_orden = request.form.get('numero_orden')
        programado = True if request.form.get('programado') == 'on' else False
        fecha_desde_str = request.form.get('fecha_desde')
        fecha_hasta_str = request.form.get('fecha_hasta')
        fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%dT%H:%M') if fecha_desde_str else None
        fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%dT%H:%M') if fecha_hasta_str else None

        # Validación de fichero cargado
        if not archivo:
            flash('No se seleccionó ningún fichero', category='NOK')
            return redirect(url_for('views.mediaplayer'))
        
        # Validación de tamaño del fichero. Máximo 200 MB
        content_length = request.content_length  
        if content_length and content_length > 200 * 1024 * 1024:
            flash('El fichero supera el máximo permitido de 200 MB', category='NOK')
            return redirect(url_for('views.mediaplayer'))

        # Numero_orden simpre >1 para dejar el 0 a los mensajes y que se muestren siempre primero, y si no se proporciona, significa que no hay prioridad, asi que asignar "999" por defecto
        if not numero_orden or numero_orden.strip() == "":
            numero_orden = "999"
        else:
            try:
                num = int(numero_orden)
                if num < 1:
                    flash("El número de orden debe ser mayor o igual a 1.", category='NOK')
                    return redirect(url_for('views.mediaplayer'))
                # Si es válido, podemos asignarlo como cadena para usarlo como prefijo
                numero_orden = str(num)
            except ValueError:
                flash("El número de orden debe ser un valor numérico.", category='NOK')
                return redirect(url_for('views.mediaplayer'))

        if programado:
            if not fecha_desde or not fecha_hasta:
                flash('Contenido programado, es obligatorio también definir rango de emisión', 'NOK')
                return render_template("mediaplayer.html", user=current_user)
            if fecha_desde > fecha_hasta:
                flash('Fecha de inicio debe ser siempre menor a la fecha de fin', 'NOK')
                return render_template("mediaplayer.html", user=current_user)
        
        # Si número de orden se ha proporcionado, se antepone como prefijo seguido de un guión bajo.
        nombre_original = secure_filename(archivo.filename)
        if numero_orden:
            nombre_ordenado = f"{numero_orden}_{nombre_original}"
        else:
            nombre_ordenado = nombre_original
        
        # Guardar el archivo en el directorio repositorio
        ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_ordenado)
        archivo.save(ruta_archivo)

        # Guardar registro en la base de datos
        ruta_relativa = f'web/static/media/{nombre_ordenado}'  # Ruta relativa para la BD, formato Linux
        nuevo_contenido = Contenido(ruta_contenido=ruta_relativa, numero_orden=numero_orden, programado=programado, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        db.session.add(nuevo_contenido)
        db.session.commit()

        flash('Contenido cargado con éxito', category='OK')
        return redirect(url_for('views.mediaplayer'))

    # GET: Mostrar el listado de los contenidos subidos
    list_contenidos = Contenido.query.order_by(Contenido.numero_orden.asc()).all() # Para mostrar el contenido por su numero de orden
    return render_template("mediaplayer.html", user=current_user, list_contenidos=list_contenidos)

# Define la ruta particular para eliminar contenido multimedia
@views.route('/mediaplayer/delmedia', methods=['GET', 'POST'])
@login_required 
def mediaplayer_delete():
    contenido_id = request.form.get('contenido_id')  # Obtiene el ID del contenido
    if not contenido_id:
        flash('ID de contenido no proporcionado.', category='NOK')
        return redirect(url_for('views.mediaplayer'))

    contenido = Contenido.query.get(contenido_id)
    
    #Creado para solucionar el problema de la ruta de los ficheros multimedia, que se duplica "web" usando current_app.root_path (paninfo\web\web\static\media\1_CABEZA.avi)
    paninfo_root = os.path.dirname(current_app.root_path) 

    # Eliminar el archivo del sistema
    ruta_archivo = os.path.join(paninfo_root, contenido.ruta_contenido)
    print(ruta_archivo)
    print(current_app.root_path)
    print(contenido.ruta_contenido)
    if os.path.exists(ruta_archivo):
        os.remove(ruta_archivo)

    # Eliminar el registro de la base de datos
    db.session.delete(contenido)
    db.session.commit()

    flash('Contenido eliminado con éxito.', category='OK')
    return redirect(url_for('views.mediaplayer'))

# Define la ruta de la creación de mensajes
@views.route('/mensajes', methods=['GET', 'POST']) 
@login_required 
def mensajes():
        if request.method == 'POST':  # Obtener los datos del formulario
            titulo = request.form.get('titulo')
            mensaje = request.form.get('mensaje')
        
            if not titulo or not mensaje:
                flash('Por favor, rellene todos los campos', category='NOK')
                return redirect(url_for('views.mensajes'))
            elif len(titulo) < 4 or len(mensaje) < 4:
                flash('Debe haber al menos 4 caracteres.', category='NOK')
                return redirect(url_for('views.mensajes'))
            else:
                new_mensaje = Mensaje(titulo=titulo, mensaje=mensaje) 
                db.session.add(new_mensaje)
                db.session.commit()
                flash('Mensaje creado', category='OK')
        
        # Listado de mensajes
        list_mensajes = Mensaje.query.all()

        return render_template("mensajes.html", user=current_user, list_mensajes=list_mensajes)

# Define la ruta particular de borrado de mensajes
@views.route('/mensajes/delmen', methods=['POST'])
@login_required
def mensajes_delete():
    # Eliminar mensaje
    mensaje_id = request.form.get('mensaje_id')
    if not mensaje_id:
        flash('No se proporcionó ID de mensaje.', category='NOK')
        return redirect(url_for('views.mensajes'))

    mensaje = Mensaje.query.get(mensaje_id)
    db.session.delete(mensaje)
    db.session.commit()
    flash('Mensaje eliminado con éxito', category='OK')

    return redirect(url_for('views.mensajes'))

# Define la ruta para la creación de mensajes prioritarios
@views.route('/prioritarios', methods=['GET', 'POST'])
@login_required 
def prioritarios():
    if request.method == 'POST':
        # El dato del campo fecha_registro se añade automáticamente en el modelo
        mensaje = request.form.get('mensaje')
        activar = request.form.get('activar')  # 'on' si la casilla está marcada
        fecha_desde = request.form.get('fecha_desde')
        fecha_hasta = request.form.get('fecha_hasta')

        activo = True if activar == 'on' else False
        # Por defecto las fechas del navegador las pasa YYYY-MM-DDTHH:MM (para type="datetime-local")
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%dT%H:%M') if fecha_desde else None
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%dT%H:%M') if fecha_hasta else None
        # Validaciones para que se rellenen las dos fechas y fecha_desde no sea mayor que hasta
        if activo:
            if not fecha_desde or not fecha_hasta:
                flash('Mensaje prioritario activado, es obligatorio también definir rango de emisión', 'NOK')
                return render_template("prioritarios.html", user=current_user)  # Ajusta tu render
            if fecha_desde > fecha_hasta:
                flash('Fecha de inicio debe ser siempre menor a la fecha de fin', 'NOK')
                return render_template("prioritarios.html", user=current_user)

        new_mensprio = MensajePrioritario(mensaje=mensaje, activo=activo, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        db.session.add(new_mensprio)
        db.session.commit()

        flash('Mensaje prioritario creado', category='OK')
        return redirect(url_for('views.prioritarios'))
    
    # Listado de mensajes prioritarios
    list_mensprio = MensajePrioritario.query.all()   

    return render_template("prioritarios.html", user=current_user, list_mensprio=list_mensprio)

# Define la ruta particular para borrar mensajes prioritarios
@views.route('/prioritarios/delprio', methods=['POST'])
@login_required
def prioritarios_delete():
    # Eliminar mensaje
    prio_id = request.form.get('prio_id')
    if not prio_id:
        flash('No se proporcionó un ID de mensaje prioritario.', 'NOK')
        return redirect(url_for('views.prioritarios'))

    mensprio = MensajePrioritario.query.get(prio_id)
    db.session.delete(mensprio)
    db.session.commit()
    flash('Mensaje prioritario eliminado.', 'OK')
    
    return redirect(url_for('views.prioritarios'))