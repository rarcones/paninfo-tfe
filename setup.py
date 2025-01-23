## SCRIPT PARA CREAR PREREQUISITOS COMO HERRAMIENTA AUXILIAR
# Crea la base de datos, usuario de instalacion y carga datos previos de PRL


# Necesario para la creacion del usuario "admin" y/o la db
import sqlite3
from werkzeug.security import generate_password_hash
import os
# Necesario para carga de datos desde el excel prerequisito
import pandas as pd
ruta_db = os.path.join('web', 'paninfo.db')
ruta_xlsx = os.path.join('.', 'cargadatos.xlsx')
usuario = input("Ingrese el nombre de usuario: ")
password = input("Ingrese la contraseña: ")
# Necesario para creacion del modelo, aunque se hace desde el script de la app,pero  por si se necesita hacerlo manualmente
from web import create_app, db

# CREACION DE LA BD
def crea_db():
    app = create_app() # Crear la aplicación Flask para utilizar el codigo de creacion de la BD
    ruta_db = os.path.join('web', 'paninfo.db') # Ruta de la base de datos
    if os.path.exists(ruta_db):
        print("La base de datos en ", ruta_db, "ya existe, no se hace nada")
        return
    
# CREACION DE USUARIO POR DEFECTO DE INSTALACION EN LA BBDD
def crea_user(u, p):
    # Conectar a la base de datos
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Verificar si el usuario de instalacion ya existe (id=1)
    cursor.execute('SELECT * FROM usuario WHERE id = 1')
    if cursor.fetchone():
        print("ERROR, El usuario de instalación ya ha sido creado previamente.")
        conn.close()
        return

    # Hash usando werkzeug
    passwordh=generate_password_hash(password)

    # Insertar el nuevo usuario en la base de datos
    cursor.execute('INSERT INTO usuario (usuario, password) VALUES (?, ?)', (usuario, passwordh))
    conn.commit()
    conn.close()
    
    print(f"Usuario '{usuario}' creado.") # Uso de f-string para mostrar el nombre del usuario

# CARGA DE DATOS PREVIOS DESDE EL CSV ENTREGADO A PRL EN LA BBDD
def crea_datos():

    # Hacer un Dataframe por cada hoja del archivo Excel
    df_empresas = pd.read_excel(ruta_xlsx, sheet_name='empresa')
    df_tipos = pd.read_excel(ruta_xlsx, sheet_name='tipo_lesion')
    df_causas = pd.read_excel(ruta_xlsx, sheet_name='causa_lesion')

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Si hay datos en las tablas, no hacer la carga (Significa que ya se ha hecho el proceso de instalacion)
    cursor.execute("SELECT COUNT(*) FROM empresa")
    num_empresas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tipo_lesion")
    num_tiposles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM causa_lesion")
    num_causasles = cursor.fetchone()[0]

    if num_empresas > 0 and num_tiposles > 0 and num_causasles > 0:
        print("ERROR, las tablas ya tienen datos.")
        conn.close()
        return # Salir de la funcion sin grabar datos

    # Si no hay datos previos, guardar datos del Dataframe en las tablas. append para hacer uso del id autoincremental de SQLite
    df_empresas.to_sql('empresa', conn, if_exists='append', index=False)
    df_tipos.to_sql('tipo_lesion', conn, if_exists='append', index=False)
    df_causas.to_sql('causa_lesion', conn, if_exists='append', index=False)

    conn.close()
    print("Datos cargados correctamente en la base de datos:")






# EJECUCION DE FUNCIONES
crea_db()
crea_user(usuario, password)
crea_datos()





