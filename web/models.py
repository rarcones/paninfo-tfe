## FICHERO CON LA DEFINICION DEL MODELO DE SQLALCHEMY QUE SE CREARÁ EN SQLITE

# La generacion del nombre de la tabla por parte de la clase de SQLAlchemy es: NombreTabla = nombre_tabla, Nombretabla = nombretabla.

from . import db # Importar db desde el propio paquete (.) el objeto db sqlalchemy que hemos definido en __init__.py. Si queremos usar esta db desde otro lado hay que importar el modulo web y su bd con "from web import db"
from flask_login import UserMixin # Clase UserMixin de flask_login para el uso de la funcion current_user
from sqlalchemy.sql import func # Clase func de sqlalchemy.sql para poder usar en este caso la funcion now() en los campos de fecha

# Tabla usuario y sus columnas
class Usuario(db.Model, UserMixin): # Clase Usuario que hereda de db.Model y módulo para que UserMixin pueda leer bd.
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria
    usuario = db.Column(db.String(50), unique=True) # Columna de tipo string, unico
    password = db.Column(db.String) # Columna de tipo string, sin límite de caracteres
    accidentes = db.relationship('Accidente', backref='usuario') # Relacion con la tabla accidente (Clase Accidente) con backref a esta tabla usuario

# Tabla causa_lesion
class CausaLesion(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    causa = db.Column(db.String(100))
    accidentes = db.relationship('Accidente', backref='causa_lesion')

# Tabla tipo_lesion
class TipoLesion(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100))
    accidentes = db.relationship('Accidente', backref='tipo_lesion')

# Tabla empresa
class Empresa(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(30), nullable=False)
    nif = db.Column(db.String(10), nullable=False, unique=True)
    accidentes = db.relationship('Accidente', backref='empresa')

# Tabla accidente
class Accidente(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id')) # Columna foreign key para relacionar y poder usar valores de la tabla usuario
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id')) # foreign key para usar valores de la tabla origen
    id_causalesion = db.Column(db.Integer, db.ForeignKey('causa_lesion.id'))
    id_tipolesion = db.Column(db.Integer, db.ForeignKey('tipo_lesion.id'))
    fecha_registro = db.Column(db.DateTime(timezone=True), default=func.now()) # Columna de tipo fecha y hora, guarda la fecha y hora actual automaticamente, no hay que añadir nada al formulario ni a la vista
    nombre_trabajador = db.Column(db.String(100)) 
    es_baja = db.Column(db.Boolean, default=False)
    fecha_baja = db.Column(db.DateTime(timezone=True), nullable=True)
    fecha_alta = db.Column(db.DateTime(timezone=True))

# Tabla contenido
class Contenido (db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    fecha_registro = db.Column(db.DateTime(timezone=True), default=func.now())
    ruta_contenido = db.Column(db.String(200)) 
    numero_orden = db.Column(db.String(200))
    programado = db.Column(db.Boolean, default=False) # Columna de tipo booleano, con el valor por defecto 0/False
    fecha_desde = db.Column(db.DateTime(timezone=True), nullable=True) # Columna de tipo fecha y hora
    fecha_hasta = db.Column(db.DateTime(timezone=True), nullable=True)
    c_visualizado = db.Column(db.Boolean, default=False) # Campo booleano creado para controlar si el contenido ya ha sido visualizado. Ayuda para el control de flujo en el bucle de crear playlist del core

# Tabla mensaje
class Mensaje (db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    titulo = db.Column(db.String(50)) 
    mensaje = db.Column(db.String(200))

# Tabla mensaje_prioritario
class MensajePrioritario (db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    fecha_registro = db.Column(db.DateTime(timezone=True), default=func.now())
    mensaje = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=False)
    fecha_desde = db.Column(db.DateTime(timezone=True))
    fecha_hasta = db.Column(db.DateTime(timezone=True))
    mp_visualizado = db.Column(db.Boolean, default=False) # Campo para controlar si el mensaje ya ha sido visualizado, por su hora de finalización. Ayuda para control de flujo en el bucle de crear playlist