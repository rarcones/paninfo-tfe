## ARRANQUE DEL MODULO CORE

import os # Importa el módulo os para acceder a funciones del sistema operativo
from datetime import datetime # Importa la clase datetime del módulo datetime, para trabajar con fechas y horas
import pymupdf # Importa el módulo pymupdf para la conversión de PDF a imagen
import time # Importa el módulo time para usar la función sleep y pausar la ejecución del programa

from web import create_app, db  # Carga del modelo de la base de datos, importa la función de creación de la app y el objeto db de nuestro paquete "web"
# Modulos de Wand para añadir el texto sobreimpresionado en las imagenes plantilla
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import subprocess # Importa el módulo subprocess para poder ejecutar y controlar procesos del sistema operativo, en este caso para VLC
import glob  # Importa el módulo glob para poder buscar usando comodines, usado para localizar ficheros de contenido y borrarlos

# Variable global para almacenar el proceso de VLC y poder usarlo desde otras funciones
proc_vlc = None 
# Hora actual
now = datetime.now() 

# Para poder acceder al modelo que tiene flask y usar sus clases de sqlalchemy
app = create_app()
app.app_context().push()




## TRATAMIENTO DE DOCUMENTOS 
# Convierte cada página de un PDF en una imagen JPG, leyendo de directorio donde se guardan los docs desde la web, y creando un subdirectorio en destino para cada directorio
# FALTA, SI YA EXISTE NO CONVERTIR y BORRAR SI YA NO HAY ORIGEN
# GENERA TODO EL CONTENIDO (PROGRAMADO Y NO PROGRAMADO) QUE HAYA EN EL DIRECTORIO Y EN LA WEB, 
# QUIEN LO MUESTRA SI ESTA EN FECHA ES PLAYLIST, QUE SOLO MUESTRA EL NO PROGRAMADO SIN FECHA, CON FECHA Y PROGRAMADO CON FECHA EN RANGO
# NO MUESTRA PROGRAMADO SIN FECHA
def convertir_docs():
    # Importar el modelo Contenido del paquete de Flask "web" (Tabla contenido)
    from web.models import Contenido

    # Define y crea el directorio de guardado de las imagenes, si no existe previamente
    dest_images = 'core/images/'
    if not os.path.exists(dest_images):
        os.makedirs(dest_images)
    
    # Obtiene todos los registros de la tabla Contenido ordenados por numero_orden, para que aparezcan en ese orden en la pantalla
    archivos = Contenido.query.order_by(Contenido.numero_orden).all()
    print(archivos)
    
    # Bucle qe itera entre los registros y solo trata los documentos PDF
    for doc in archivos:
        # La columna ruta_contenido almacena la ruta relativa donde la web deja los ficheros, y el nombre del fichero
        ruta_relativa = doc.ruta_contenido
        # Solo PDF, si no, sale del bucle.
        if not ruta_relativa.lower().endswith('.pdf'):
            continue
        # Construir la ruta completa del PDF
        ruta_pdf = os.path.join(ruta_relativa)
        # Control de errores. Verifica que el fichero exista, si no, sale del bucle. Puede ser que se haya eliminado del repositorio desde el sistema operativo.
        if not os.path.exists(ruta_pdf):
            print(f"El archivo PDF no existe: {ruta_pdf}")
            continue

        # Crear un subdirectorio por cada PDF, usando el nombre del fichero (sin extensión), para dejar las imágenes/páginas
        nombre_fichero, _ = os.path.splitext(os.path.basename(ruta_relativa))
        subdirectorio_archivo = os.path.join(dest_images, nombre_fichero)
        if not os.path.exists(subdirectorio_archivo):
            os.makedirs(subdirectorio_archivo)

        # Abrir el PDF con PyMuPDF, y generar una imagen por página, con control de errores
        try:
            documento = pymupdf.open(ruta_pdf)
        except Exception as e:
            print(f"Error al abrir {ruta_pdf}: {e}")
            continue

        total_paginas = len(documento)
        print(f"Procesando '{ruta_pdf}', total de páginas: {total_paginas}")
    
        # Iterar sobre cada página del PDF
        for num_pagina in range(total_paginas):
            nombre_imagen = f'pagina_{num_pagina + 1}.jpg'
            ruta_imagen = os.path.join(subdirectorio_archivo, nombre_imagen)
            
            # Control de ficheros existentes: omitir si la imagen ya existe
            if os.path.exists(ruta_imagen):
                print(f"La imagen ya existe y se omite: {ruta_imagen}")
                continue
            
            try:
                pagina = documento.load_page(num_pagina)  # Carga la página
                pix = pagina.get_pixmap(dpi=300)         # Renderiza la página a imagen con 300 DPI
                pix.save(ruta_imagen)                     # Guarda la imagen en formato JPG
                print(f"Guardada: {ruta_imagen}")
            except Exception as e:
                print(f"Error procesando la página {num_pagina + 1} del archivo {ruta_pdf}: {e}")
        
        # Cierra el documento
        documento.close()




## CALCULO DE NUMERO DE DIAS SIN ACCIDENTES
# Calcula el número de días transcurridos entre la fecha de ejecución y la de el último accidente registrado
def calcular_dias():
    # Importar el modelo Accidente para poder consultar la tabla accidente
    from web.models import Accidente

    # Obtener el primer registro que tenga fecha_baja y sea la más reciente, con orden descendente
    ultimo_acc = (Accidente.query
                       .filter(Accidente.fecha_baja.isnot(None))
                       .order_by(Accidente.fecha_baja.desc())
                       .first())
    
    if ultimo_acc is not None:
        # Fecha de ahora sin formato local para poder hacer los cálculos
        ahora = datetime.now()
        # Se resta la fecha de hoy la del ultimo accidente y se obtiene los dias transcurridos. El resultado es un objeto timedelta
        diferencia = ahora - ultimo_acc.fecha_baja
        # Se usa el atributo days del timedelta para obtener los días transcurridos  
        dias_transcurridos = diferencia.days
        print(f"Días sin accidentes: {dias_transcurridos} días")
        
        return dias_transcurridos




## CALCULO DE MAXIMO NUMERO DE DIAS SIN ACCIDENTES
def calcular_maximo():
    # Importar el modelo Accidente para poder consultar la tabla accidente
    from web.models import Accidente

    # Obtener todos los registros tenga fecha_baja en orden ascendente
    accidentes = (Accidente.query
                  .filter(Accidente.fecha_baja.isnot(None))
                  .order_by(Accidente.fecha_baja.asc())
                  .all())
    
    # Si no hay registros, o son menos de 2, no se calcula
    if not accidentes or len(accidentes) < 2:
        return 0
    
    # Inicializar la variable que almacena el rango
    maximo_dias = 0
    
    # Iterar sobre la lista de accidentes (desde el segundo en adelante)
    for i in range(1, len(accidentes)):
        # Calcular la diferencia en días entre un accidente y el anterior
        diff = (accidentes[i].fecha_baja - accidentes[i-1].fecha_baja).days
        # Si la diferencia de la ocurrencia es mayor al máximo actual, se actualiza
        if diff > maximo_dias:
            maximo_dias = diff
    print(f"Máximo número de días sin accidentes: {maximo_dias}")
    return maximo_dias




## CREACION IMAGEN CALCULO DIAS TRANSCURRIDOS Y MAXIMO DIAS SIN ACCIDENTES
def crear_img_dias(transcurridos, maximo):
# Recibe como parámetros el número de días transcurridos y el máximo de días sin accidentes y los sobreimpresiona en la plantilla

    # Convertir los valores de las variables de los días calculados a cadena
    dtranscurridos = str(transcurridos)
    dmaximo = str(maximo)
    
    # Variables de la ruta de la imagen plantlla (PNG), y de la imagen resultante con los textos
    ruta_imagen_base = 'core/source/plantilla.png'
    ruta_imagen_resultado = 'core/images/0_dias_sin_accidentes.png'
    
    # Edita la imagen y "dibuja" el texto con funciones de Wand
    with Image(filename=ruta_imagen_base) as img:
        with Drawing() as draw:
            # Tipo de letra, tamaño y color del texto para los días sin accidentes
            draw.font_size = 140
            draw.fill_color = Color('#ffffff')
            # Coloca el texto mediante coordenadas en píxeles
            texto_dias = f"{dtranscurridos} DÍAS SIN ACCIDENTES" # Texto con el calculo
            draw.text(80, 500, texto_dias)
            
            # Tipo de letra, tamaño y color del texto para el máximo de días sin accidentes
            draw.font_size = 110
            draw.fill_color = Color('#ffffff')
            # Coloca el texto mediante coordenadas en píxeles
            texto_maximo = f"Máximo histórico: {dmaximo} días"
            draw.text(400, 800, texto_maximo)
            
            # Aplicar el dibujo,que es el texto, sobre la imagen
            draw(img)
        
        # Guardar la imagen resultante en la ruta especificada
        img.save(filename=ruta_imagen_resultado)




## CREACION DE LAS IMAGENES PARA MOSTRAR LOS MENSAJES
# Crea una imagen por cada mensaje de la tabla, sobreimpresionando el texto en la plantilla
def crear_img_mensajes():
    # Importa el modelo Mensaje para el acceso a los datos de la tabla
    from web.models import Mensaje

    # Variables de la ruta de la imagen plantlla (PNG), y del directorio de salida
    ruta_imagen_base = 'core/source/plantilla.png'
    ruta_imagen_resultado = 'core/images/'
    # Consultar todos los registros de la tabla Mensaje, si no hay registros, se muestra un mensaje y se sale de la función (como debugging)
    mensajes = Mensaje.query.all()
    if not mensajes:
        print("No se encontraron registros en la tabla Mensaje.")
        return
    
    # Realiza una limpieza de las imagenes previas, para que cada ejecución genere solo las imágenes actuales
    borra_previo = os.path.join(ruta_imagen_resultado, "0_mensaje_id_*")
    for existente in glob.glob(borra_previo):
        os.remove(existente)
    
    # Itera sobre los mensajes y crear una imagen por cada uno
    for men in mensajes:
        # Edita la imagen y "dibuja" el texto con funciones de Wand
        with Image(filename=ruta_imagen_base) as img:
            with Drawing() as draw:
                # Tipo de letra, tamaño y color del texto para el título del mensaje
                draw.font_size = 110
                draw.fill_color = Color('#ffffff')
                # Coloca el texto mediante coordenadas en píxeles
                draw.text(60, 500, men.titulo)
                
                # Tipo de letra, tamaño y color del texto para el mensaje
                draw.font_size = 60
                draw.fill_color = Color('#ffffff')
                # Coloca el texto mediante coordenadas en píxeles
                draw.text(80, 620, men.mensaje)
                
                # Aplicar el dibujo sobre la imagen
                draw(img)
            
            # Crea la ruta y el fichero de salida  para el mensaje
            output_path = os.path.join(ruta_imagen_resultado, f"0_mensaje_id_{men.id}.png")
            img.save(filename=output_path)
            #print(f"Imagen creada del id:{men.id} en {output_path}")




## CREACION DE LAS IMAGENES PARA MOSTRAR LOS MENSAJES PRIORITARIOS
# Crea una imagen por cada mensaje prioritario que entre en la lógica de la programación, y sobreimpresiona el texto en la plantilla

def crear_img_prioritario():
    # Importa el modelo MensajePrioritario para el acceso a los datos de la tabla mensaje_prioritario
    from web.models import MensajePrioritario

    # Definir la ruta de la imagen plantilla y del directorio de salida
    ruta_imagen_base = 'core/source/prioritaria.png'
    ruta_imagen_resultado = 'core/prioritary/'
    # Consultar todos los registros de la tabla mensaje, que tenga el checkbox activado y que la fecha actual esté en el rango de fechas definidas
    prioritarios = MensajePrioritario.query.filter( MensajePrioritario.activo == True, MensajePrioritario.fecha_desde <= now, MensajePrioritario.fecha_hasta >= now ).all()
    
    # Realiza una limpieza de las imagenes previas, para que cada ejecución genere solo las imágenes actuales
    borra_previo = os.path.join(ruta_imagen_resultado, "0_prioritario_id_*")
    for existente in glob.glob(borra_previo):
        os.remove(existente)

    for prio in prioritarios:
        # Abrir la imagen plantilla
        with Image(filename=ruta_imagen_base) as img:
            with Drawing() as draw:
                # Tipo de letra, tamaño y color del texto para el título del mensaje prioritario
                draw.font_size = 140
                draw.fill_color = Color('#ff5a47')

                # Coloca el texto mediante coordenadas en píxeles
                draw.text(60, 700, prio.mensaje)

                # Aplicar el dibujo sobre la imagen
                draw(img)

            # Crea la ruta y el fichero de salida  para el mensaje
            output_path = os.path.join(ruta_imagen_resultado, f"0_prioritario_id_{prio.id}.png")            
            #print(f"0_prioritario_id_{prio.id}")
            img.save(filename=output_path)
            #print(f"Imagen creada del id:{men.id} en {output_path}")




## CREACION DEL FICHERO DE PLAYLIST
#Por un lado los contenidos subidos por el usuario y por otro los generados en tiempo de ejecucion con los mensajes

def crear_playlist():
    # Importa el modelo Contenido para el acceso a los datos de la tabla
    from web.models import Contenido
    
    # Variable para definir la ruta raiz de los ficheros, partiendo que base_dir es el directorio donde se encuentra el arranque del core, core.py
    base_dir = os.getcwd()
    # Ruta de creación de la playlist     
    output_dir = os.path.join(base_dir, "core")
    # Ruta de los ficheros de contenido de imágenes, mas los de mensajes 
    images_dir = os.path.join(base_dir,  "core", "images")
    # Crea otra variable con el mismo valor que images_dir, para poder hacer el cambio de directorio en la generacion de la playlist
    msg_dir = images_dir
    # Ruta de creación del fichero de playlist
    playlist_filename = os.path.join(output_dir, "playlist.m3u")
    #print("Base_dir es "+ base_dir)
    #print("Output_dir es "+ output_dir)
    #print("Images_dir es "+images_dir)
    #print("playlist_filename es "+playlist_filename)
    # Creación del fichero de playlist, con el texto de cabecera M3U para que VLC lo reconozca como playlist
    playlist_lines = ["#EXTM3U"]
    # Variable con la hora actual para la lógica de programación
    now = datetime.now()
    
    # Obtener todos los contenidos dados de alta en la tabla, ordenados por numero_orden
    contenidos = Contenido.query.order_by(Contenido.numero_orden).all()
    
    ## GENERACION DE LAS LINEAS DE LA PLAYLIST DE LOS FICHEROS DE CONTEO DE DIAS Y MENSAJES 
    # print(msg_dir)

    # Bucle for que por cada fichero en /core/images/, ordenado con sorted por nombre para que primero salgan los "0" que son el fichero de conteo de dias y los mensajes, crea una línea en la playlist
    for file in sorted(os.listdir(msg_dir)):
            # Si el fichero empieza por "0_" y es un fichero (No es un directorio), se añade a la playlist  
            if file.startswith("0_") and os.path.isfile(os.path.join(msg_dir, file)):
                # Ruta de la playlist
                file_path = os.path.join(msg_dir, file)
                # Añade la línea a la playlist, junto con una pausa extra de 2 segundos. Por defecto VLC reproduce las imágenes durante 10 segundos
                playlist_lines.append(f"{file_path}\nvlc://pause:2")
                # print("ruta_imagenes_plantilla es", file_path) 

    ## GENERACION DE LAS LINEAS DE LA PLAYLIST DE LOS FICHEROS DE CONTENIDO
    # Bucle for que revisa para cada registro insertado, si se han definido fechas y esta en rango
    for cont in contenidos:
        # Si el registro está marcado como programado:
        if cont.programado:
            # Si no se han definido las fechas pero esta programado, no se muestra, sale del bucle
            if not (cont.fecha_desde and cont.fecha_hasta): 
                continue
            # Si no  está en rango de programación, no se muestra, sale del bucle
            if not (cont.fecha_desde <= now <= cont.fecha_hasta): 
                continue

        # Si se continua, es que el registro no esta programado, ya ha sido visualizado, y fecha_hasta es anterior a fecha de ejecucion. Es decir, ya se ha visualizado en el pasado. Se sale del bucle
        else:
            # (Ajusta el nombre del campo si no existe "visualizado")
            # Si cont está “visualizado” y la fecha_hasta ya pasó => excluir
            if cont.c_visualizado and cont.fecha_hasta and cont.fecha_hasta < now:
                continue
        # ruta_relativa = os.path.normpath(cont.ruta_contenido)
        # print("Solucion ruta relativa es "+ruta_relativa)
        # print("Sin solucion seria "+ os.path.normpath(cont.ruta_contenido) )

        # Comprobamos si el registro en BD con la ruta y nombre del fichero contiene la cadena "pdf" (La extensión .pdf)
        if "pdf" in cont.ruta_contenido.lower():
            # Define el nombre base del PDF, sin la extensión. Se asume que el subdirectorio con las imágenes está en core/images/<nombre_base_del_pdf>/
            base_pdf_name = os.path.splitext(os.path.basename(cont.ruta_contenido))[0]
            #print("Base_pdf_name es "+base_pdf_name)
            # Variable que compone la ruta del directorio de imágenes con el directorio del pdf
            images_dir = os.path.join(base_dir, "core", "images", base_pdf_name)
            #print("Images_dir ahora es "+images_dir)
            # Si no existe el directorio de imágenes, se omite el registro. Puede que haya sido borrado manualmente en el SO
            if not os.path.exists(images_dir):
                #print(f"No se encontró el directorio de imágenes para: {cont.ruta_contenido}")
                continue
            
            # Bucle for que lista y ordena las imágenes del directorio de cada documento pdf
            for image in sorted(os.listdir(images_dir)):
                # Si la imagen es un archivo (no un directorio) y tiene una extensión permitida de imagen (Por diseño el programa de conversion de pdfs genera jpg)
                if image.lower().endswith(('.jpg', '.jpeg', '.png')):
                    # Genera la ruta completa para leer la imagen
                    full_path = os.path.join(images_dir, image)
                    #print("Full_path es "+full_path)
                    # Agrega la línea de la imagen a la playlist, junto con una pausa extra de 6 segundos
                    playlist_lines.append(f"{full_path}\nvlc://pause:6")
        else:
            # Para otros tipos de contenido (por ejemplo, vídeos) se utiliza la ruta original, para no tener que mover ficheros mas pesados y no requieren procesado extra
            file_path = os.path.join(base_dir, cont.ruta_contenido)
            #print("File_path es"+file_path)
            # Si no existe el fichero
            if not os.path.exists(file_path):
                print(f"El fichero no existe: {file_path}")
                continue
            # Agrega la línea del video a la playlist, junto con una pausa extra de 1 segundo, como pequeña transición entre videos
            playlist_lines.append(f"{file_path}\nvlc://pause:1")
  
    # Escritura de todas las lineas generadas al fichero de playlist
    with open(playlist_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))
    
    print("Playlist generada en:", playlist_filename)




## CREACION DE LA PLAYLIST DE PRIORITARIOS
# Crea una playlist con las imágenes de los mensajes prioritarios aexistentes en el directorio

def crear_playlistprio():
    # Variable para definir la ruta raiz de los ficheros de mensajes prioritarios
    base_dir = os.getcwd()
    # Ruta de creación de la playlist de prioritarios
    output_dir = os.path.join(base_dir, "core")
    # Nombre del fichero de playlist de prioritarios
    playlist_filename = os.path.join(output_dir, "playlist_prio.m3u")

    # Creación del fichero de playlist, con el texto de cabecera M3U para que VLC lo reconozca como playlist
    playlist_lines = ["#EXTM3U"]

    # Diccionario para las rutas base y sus respectivas extensiones válidas definidas. El formato es, clave "core/prioritary" y valor {'.png', '.jpg'}
    ruta_base = { os.path.join(base_dir, "core", "prioritary"): {'.png', '.jpg'} }

    # Recorrer cada ruta base y sus extensiones válidas
    for ruta, valid_extensions in ruta_base.items():
        # Si no existe la ruta, se muestra un mensaje y se salta a la siguiente iteración, modo debugging manual
        if not os.path.exists(ruta):
            print(f"La ruta no existe: {ruta}")
            continue
        # Bucle que recorre cada ruta, directorio y fichero de la ruta base
        for root, dirs, files in os.walk(ruta):
            # Por cada fichero
            for file in files:
                # Se separa la extensión del fichero y se convierte a minúsculas (Indice [0] sería el nombre del fichero, [1] es la extensión)
                ext = os.path.splitext(file)[1].lower()
                # print ("extension es", ext)
                # Si la extensión está en la lista de extensiones válidas
                if ext in valid_extensions:
                    # Se genera la ruta completa del fichero de imagen
                    file_path = os.path.join(root, file)
                    # print(file_path + " es filepath")
                    # Se añade la línea a la playlist
                    playlist_lines.append(file_path)

    # Escritura de todas las lineas generadas al fichero de playlist de prioritarios
    with open(playlist_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))
    
    print("Playlist generada en:", playlist_filename)




## EJECUCION VLC
# Mediante el módulo subprocess, para tener un control extra sobre el servicio, se ejecuta VLC con la playlist recibida como parámetro
# NOTA: Como VLC esta en modo dummy, no se ve la interfaz de VLC, para salir de la visualizacion del contenido hay que pulsar "s" y para salir de VLC hay que pulsar ctrl + "q"

def vlc(playl):

    # Definir el directorio fijo donde se encuentran las playlists
    base_dir = os.getcwd()
    playlist_path = os.path.join(base_dir, "core", playl)
    # Para hacer uso de la variable global
    global proc_vlc 
    
    # Verificar que la playlist existe
    if not os.path.exists(playlist_path):
        print(f"La playlist no se encontró en: {playlist_path}")
        return

    try:
        # Ejecutar VLC pasando la ruta de la playlist.
        # Si VLC está en el PATH, basta con 'vlc'
        #subprocess.Popen(["vlc", playlist_path])
        #print(f"VLC se inició para reproducir: {playlist_path}")
        # Si "vlc" no está en el PATH, se debe utilizar la ruta completa al ejecutable.
        # Por ejemplo en Windows podría ser:
        proc_vlc=subprocess.Popen(["vlc", "--video-title-timeout=0", "--intf", "dummy", "--loop", "--fullscreen",  playlist_path])
        print(f"VLC se inició para reproducir: {playlist_path}")

    except Exception as e:
        print("Error al iniciar VLC:", e)
        proc_vlc = None
    return proc_vlc

# Ejecución manual, como debugging    
#vlc("playlist.m3u")
#vlc("playlist_prio.m3u")




## PARADA VLC
# Hace la función de reinicio, si ya hay un proceso en ejecución, lo termina usando terminate() y luego inicia un nuevo proceso con la playlist que corresponde
def parar_vlc():

    # Para hacer uso de la variable global
    global proc_vlc
    # Si existe un proceso VLC en ejecución, lo termina
    if proc_vlc is not None:
        print("Terminando la instancia actual de VLC...")
        # Envía la señal para terminar el proceso.
        proc_vlc.terminate()  
        try:
            # Tiempo extra para dar margen a que el proceso finalice.
            proc_vlc.wait(timeout=10)
            print("VLC finalizado correctamente.")
        # Si no termina en el tiempo establecido, mata el proceso 
        except subprocess.TimeoutExpired:
            print("VLC no se detiene; se fuerza la parada.")
            proc_vlc.kill()
            proc_vlc.wait()
        proc_vlc = None

    # Dar un pequeño retraso para asegurar que el sistema libere recursos antes de iniciar un nuevo proceso.
    time.sleep(10)

    # Iniciar VLC con la playlist nueva.
    #return vlc()




## CONTROL DE CONTENIDOS PROGRAMADOS
# Gestiona que contenido se emite en base a ciertos parámetros, ejecutando las funciones requeridas para rehacer los contenidos que se van a mostrar

def control_emision():
    # Importa los modelos necesarios para acceder a las tablas de contenido y mensajes prioritarios, que son las que generan sus playlists
    from web.models import MensajePrioritario, Contenido

    # Fecha actual, necesario para saber que se debe reproducir en cada ejecución de la función
    now = datetime.now() 
    # print("Hora ciclo control:", now)
    # Filtro de mensajes prioritarios que, estén activos, no hayan sido visualizados y en rango de fechas en el momento de la ejecución
    es_prioritario = MensajePrioritario.query.filter( MensajePrioritario.activo == True, MensajePrioritario.mp_visualizado == False, MensajePrioritario.fecha_desde <= now, MensajePrioritario.fecha_hasta >= now ).all()
    # Filtro de contenidos que,estén programados, No hayan sido visualizados, contengan datos de fecha_desde y fecha_hasta y en rango de fechas en el momento de la ejecución (que significa que estan programados en ese momento)
    es_programado = Contenido.query.filter( Contenido.programado == True, Contenido.c_visualizado == False, Contenido.fecha_desde != None, Contenido.fecha_hasta != None, Contenido.fecha_desde <= now, Contenido.fecha_hasta >= now ).all()
    
    ## BLOQUE DE MENSAJES PRIORITARIOS
    # Si hay mensajes que coinciden con el filtrado anterior hay que emitirlos, por lo que se ejecutan las funciones correspondientes de creación, generación y ejecución de playlist de prioritarios, y se activa la marca de visualizado para que no se vuelva a emitir en el futuro
    if es_prioritario:
        for prioact in es_prioritario:
            prioact.mp_visualizado = True
        db.session.commit()
        #print("Se ha detectado contenido prioritario activo en el rango de fechas.")
        crear_img_prioritario()
        crear_playlistprio()
        parar_vlc()
        vlc("playlist_prio.m3u")
        time.sleep(10)
        
    # Filtra los mensajes prioritarios que, estén activos, hayan sido visualizados y la fecha_hasta la que se debe emitir es anterior a la fecha de ejecución, con lo cual hay que eliminarlo de la lista de reproducción y marcarlo como inactivo.   
    prioritario_caducado = MensajePrioritario.query.filter( MensajePrioritario.activo == True, MensajePrioritario.mp_visualizado == True, MensajePrioritario.fecha_hasta < now ).all()
    # Para ello, se ejecutan las funciones correspondientes y se ejecuta VLC, pero con la playlist de contenidos. En el caso de haber mas de un mensaje prioritario, en la siguiente ejecución, volvera a crearse y emitirse la playlist de prioritarios
    if prioritario_caducado:
        for priocad in prioritario_caducado:
            priocad.activo = False
        db.session.commit()
        #print("Eliminando contenido prioritario fuera del rango de fechas.")
        crear_img_prioritario()
        crear_playlistprio()
        parar_vlc()
        vlc("playlist.m3u")
        time.sleep(10)

    ## BLOQUE DE CONTENIDO PROGRAMADO
    # Si hay mensajes que coinciden con el filtrado anterior hay que emitirlos, por lo que se ejecutan las funciones correspondientes de creación, generación y ejecución de playlist de contenidos, y se activa la marca de visualizado para que no se vuelva a emitir en el futuro
    if es_programado:
        for progact in es_programado:
            progact.c_visualizado = True
        db.session.commit()
        #print("Se ha detectado contenido programado activo en el rango de fechas.")
        convertir_docs()
        crear_playlist()
        parar_vlc()
        vlc("playlist.m3u")
        time.sleep(10)


    # Filtra los contenidos que, estén programados, hayan sido visualizados y la fecha_hasta la que se debe emitir es anterior a la fecha de ejecución, con lo cual hay que eliminarlo de la lista de reproducción y marcarlo como caducado para no mostrarse en el siguiente ciclo.   
    programado_caducado = Contenido.query.filter( Contenido.programado == True, Contenido.c_visualizado == True, Contenido.fecha_hasta < now ).all()
    if programado_caducado:
        for priocad in programado_caducado:
            priocad.programado = False
        db.session.commit()
        #print("Eliminando contenido fuera del rango de fechas.")
        convertir_docs()
        crear_playlist()
        parar_vlc()
        vlc("playlist.m3u")
        time.sleep(10)
    
    return 



## ACTUALIZACION CONTEO DE DIAS
# Función creada para ejecutarse mediante la tarea programada con schedule. Ejecuta la función de crear la imagen con los datos de los dias actualizados para el día en curso.

def update_dias():
    #print("Ejecucion de la tarea programada, hora", now)
    crear_img_dias(calcular_dias(),calcular_maximo())
    parar_vlc()




#####################################
##################### INICIO DEL CORE
#####################################

def inicio():
    print("Hora de primera ejecución", now)
    import time
    import schedule
    convertir_docs()
    crear_img_dias(calcular_dias(),calcular_maximo())
    crear_img_mensajes()
    crear_img_prioritario()
    crear_playlist()
    crear_playlistprio()
    schedule.every().day.at("00:06").do(update_dias)
    vlc("playlist.m3u") # Se inicia con playlist normal

    while True:
        control_emision()
        schedule.run_pending() # Gestiona las tareas pendientes, en este caso, el update dias
        time.sleep(60) 


if __name__ == '__main__':
    # Ejecuta el origen del programa
    inicio()

############################################
## EJECUCION MANUAL DE FUNCIONES
############################################

##convertir_docs()
#calcular_dias()
#calcular_maximo()
##crear_img_dias(calcular_dias(),calcular_maximo())
##crear_img_mensajes()
##crear_img_prioritario()
##crear_playlist()
##crear_playlistprio()
#vlc(playl)
##control_emision()
#reiniciar_vlc()
