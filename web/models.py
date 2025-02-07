## FICHERO CON LA DEFINICION DEL MODELO DE SQLALCHEMY QUE SE CREARÁ EN SQLITE
# La generacion automática de los nombre de la tabla por parte de la clase de SQLAlchemy es: NombreTabla = nombre_tabla, Nombretabla = nombretabla.

from . import db # Importar db desde el propio paquete (.) el objeto db sqlalchemy que hemos definido en __init__.py. Si queremos usar esta db desde otro lado hay que importar el modulo web y su bd con "from web import db"
from flask_login import UserMixin # Clase UserMixin de flask_login para el uso de la funcion current_user
from sqlalchemy.sql import func # Clase func de sqlalchemy.sql para poder usar en este caso la funcion now() en los campos de fecha

# Tabla "usuario"
class Usuario(db.Model, UserMixin): # Clase Usuario que hereda de db.Model y módulo para que UserMixin pueda leer la BD e identificar los usuarios.
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    usuario = db.Column(db.String(50), unique=True) # Columna de tipo string, valor único.
    password = db.Column(db.String) # Columna de tipo string, sin límite de caracteres.
    accidentes = db.relationship('Accidente', backref='usuario') # Codigo para la relacion con la tabla accidente (Clase Accidente) con backref a esta tabla usuario.

# Tabla "causa_lesion"
class CausaLesion(db.Model): 
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    causa = db.Column(db.String(100)) # Columna de tipo string, con un límite de 100 caracteres.
    accidentes = db.relationship('Accidente', backref='causa_lesion') # Codigo para la relacion con la tabla accidente (Clase Accidente) con backref a esta tabla causa_lesion.

# Tabla "tipo_lesion"
class TipoLesion(db.Model): 
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    tipo = db.Column(db.String(100)) # Columna de tipo string, con un límite de 100 caracteres.
    accidentes = db.relationship('Accidente', backref='tipo_lesion') # Codigo para la relacion con la tabla accidente (Clase Accidente) con backref a esta tabla tipo_lesion.

# Tabla "empresa"
class Empresa(db.Model): 
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    nombre_empresa = db.Column(db.String(30), nullable=False) # Columna de tipo string, con un límite de 30 caracteres, no puede estar vacío.
    nif = db.Column(db.String(10), nullable=False, unique=True) # Columna de tipo string, valor único, con un límite de 10 caracteres, no puede estar vacío.
    accidentes = db.relationship('Accidente', backref='empresa') # Codigo para la relacion con la tabla accidente (Clase Accidente) con backref a esta tabla empresa.

# Tabla accidente
class Accidente(db.Model): 
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id')) # Columna foreign key para relacionar y poder usar los datos de la tabla usuario.
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id')) # Columna foreign key para relacionar y poder usar los datos de la tabla empresa.
    id_causalesion = db.Column(db.Integer, db.ForeignKey('causa_lesion.id')) # Columna foreign key para relacionar y poder usar los datos de la tabla causa_lesion.
    id_tipolesion = db.Column(db.Integer, db.ForeignKey('tipo_lesion.id')) # Columna foreign key para relacionar y poder usar los datos de la tabla tipo_lesion.
    fecha_registro = db.Column(db.DateTime(timezone=True), default=func.now()) # Columna de tipo fecha y hora, guarda la fecha y hora actual automaticamente al insertar registro.
    nombre_trabajador = db.Column(db.String(100)) # Columna de tipo string, con un límite de 100 caracteres.
    es_baja = db.Column(db.Boolean, default=False) # Columna de tipo booleano, con el valor por defecto 0/False.
    fecha_baja = db.Column(db.DateTime(timezone=True), nullable=True) # Columna de tipo fecha y hora, con zona horaria local, puede estar vacío.
    fecha_alta = db.Column(db.DateTime(timezone=True)) # Columna de tipo fecha y hora, con zona horaria local.

# Tabla contenido
class Contenido (db.Model): 
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    fecha_registro = db.Column(db.DateTime(timezone=True), default=func.now()) # Columna de tipo fecha y hora, guarda la fecha y hora actual automaticamente al insertar registro.
    ruta_contenido = db.Column(db.String(200))  # Columna de tipo string, con un límite de 200 caracteres.
    numero_orden = db.Column(db.String(200)) # Columna de tipo string, con un límite de 200 caracteres.
    programado = db.Column(db.Boolean, default=False) # Columna de tipo booleano, con el valor por defecto 0/False.
    fecha_desde = db.Column(db.DateTime(timezone=True), nullable=True) # Columna de tipo fecha y hora, con zona horaria local, puede estar vacío.
    fecha_hasta = db.Column(db.DateTime(timezone=True), nullable=True) # Columna de tipo fecha y hora, con zona horaria local, puede estar vacío.
    c_visualizado = db.Column(db.Boolean, default=False) # Campo booleano creado para controlar si el contenido ya ha sido visualizado. Ayuda para el control de flujo en el bucle de crear playlist del core.

# Tabla mensaje
class Mensaje (db.Model): 
    id = db.Column(db.Integer, primary_key=True)  # Columna de tipo integer, clave primaria.
    titulo = db.Column(db.String(50))  # Columna de tipo string, con un límite de 50 caracteres.
    mensaje = db.Column(db.String(200)) # Columna de tipo string, con un límite de 200 caracteres.

# Tabla mensaje_prioritario
class MensajePrioritario (db.Model):
    id = db.Column(db.Integer, primary_key=True) # Columna de tipo integer, clave primaria.
    fecha_registro = db.Column(db.DateTime(timezone=True), default=func.now()) # Columna de tipo fecha y hora, guarda la fecha y hora actual automaticamente al insertar registro.
    mensaje = db.Column(db.String(200)) # Columna de tipo string, con un límite de 200 caracteres
    activo = db.Column(db.Boolean, default=False) # Columna de tipo booleano, con el valor por defecto 0/False.
    fecha_desde = db.Column(db.DateTime(timezone=True)) # Columna de tipo fecha y hora, con zona horaria local.
    fecha_hasta = db.Column(db.DateTime(timezone=True))  # Columna de tipo fecha y hora, con zona horaria local.
    mp_visualizado = db.Column(db.Boolean, default=False) # Campo para controlar si el mensaje ya ha sido visualizado, por su hora de finalización. Ayuda para control de flujo en el bucle de crear playlist