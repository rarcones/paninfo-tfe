# paninfo-tfe

Proyecto para el Trabajo Fin de Estudios (TFE)  del Grado en Ingeniería Informática de la Universidad Internacional de la Rioja (UNIR).

El proyecto se basa en la creación de una aplicación de cartelería digital que muestre información diversa relativa al entorno industrial donde se vaya a instalar, principalmente procedimientos y protocolos de seguridad y salud, y también información general como videos de concienciación, avisos de última hora, eventos en la instalación industrial e información similar.

Usando Python como lenguaje principal, y sobre una distribución Linux en cualquier PC disponible, se unen diferentes módulos y librerías para crear un software que lea la información recopilada de entrada, la transforme y la prepare para ser mostrada en una pantalla.



## Funcionamiento
El sistema se compone de dos módulos diferenciados, para un sistema operativo Linux, que trabajando conjuntamente conforman el sistema.

**WEB:** Este módulo hace la función de GUI. Mediante una aplicación Flask completa, el usuario puede subir y crear el contenido que se desea mostrar en la pantalla. 

**CORE:** Este módulo hace la función de "backend", lee el contenido disponible en el repositorio y, acorde a ciertas reglas de programación, crea listas de reproducción que VLC cargará y reproducirá.



## Componentes
El sistema utiliza los siguientes componentes principales:  
-Python  
-Flask  
-Gunicorn  
-SQLite  
-VLC  
-PyMuPDF  
-Wand  



## Preparacion entorno pruebas
El proyecto ha sido desarrollado en una distribución Linux con entorno gráfico Ubuntu 24.04 LTS, que proporciona soporte de los componentes a largo plazo.
Una vez descargado el fichero comprimido con la aplicación, se deben seguir unos pasos a modo de preparacion e instalación.

### Aplicaciones del S.O. Linux:
-sudo apt install python3 python3-venv python3-pip  
-sudo apt install libmagickwand-dev vlc  

### Creación entorno virtual Python para este proyecto, ubicándose en la ruta raiz donde se encuentren los ficheros:
cd /home/_usuario_/paninfo/  
-python3 -m venv venv_tfe

### Activación entorno virtual:
-source venv_tfe/bin/activate

### Instalación librerías Python necesarias, con entorno virtual cargado, recopiladas en el fichero paquetes_pip.txt:
-pip install -r paquetes_pip.txt  
En caso de no haber cargado el entorno virtual, es necesario utilizar su intérprete de Python, lo ejecutaremos así:  
-/home/_usuario_/paninfo/venv_tfe/bin/python -m pip install -r paquetes_pip.txt



## Ejecución en entorno pruebas
Se deberá ejecutar, por un lado el módulo web dentro del directorio raiz y con el entorno virtual cargado 
el comando python main.py. Esto mostrará un mensaje con la URL a la que acceder desde el navegador.
Para el módulo core, se ejecutará por otro lado, en otra ventana de consola el comando python core.py, que leerá los repositorios 
y creará y mostrará la información almacenada.

Si queremos usar directamente los binarios del entorno virtual (En algú script, por ejemplo) sin haberlo cargado previamente:  
-/home/_usuario_/paninfo/venv_tfe/bin/python main.py  
-/home/_usuario_/paninfo/venv_tfe/bin/python core.py  



## Ejecución en entorno productivo
Para la ejecución del módulo web, es recomendable utilizar un protocolo seguro de comunicación. Lo mas sencillo para el proyecto es generar un certificado SSL autofirmado que el servidor Gunicorn utilizará para usar HTTPS. Con este comando se genera para una duración de 5 años:  
-openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 1460

Una vez creado, para ejecutar la aplicación Flask del panel informativo de forma segura en Gunicorn: 
 -gunicorn --certfile=/_ruta certificados_/cert.pem  --keyfile=/_ruta certificados_/key.pem --workers 2 --bind 0.0.0.0:443 main:app 

Se recomienda la ejecución del módulo web como servicio systemd en el sistema operativo.

Para la ejecución del módulo core, se recomienda crear un fichero .desktop en el directorio del usuario _~/.config/autostart/_ para que el programa arranque con el inicio de sesión y carga del entorno gráfico del usuario.  

Los pasos a seguir, son crear el directorio autostart (En Ubuntu LTS no existe por defecto) y crear el fichero:  
-mkdir -p ~/.config/autostart  
-nano ~/.config/autostart/paninfocore.desktop  

Añadimos al fichero .desktop:  

[Desktop Entry]
Type=Application
Name=PaninfoCore
Comment=Core para gestión de contenidos del panel informativo
Path=/home/_usuario_/paninfo
Exec=/home/_usuario_/paninfo/venv_tfe/bin/python core.py
Terminal=false  

Se debe permitir que el usuario que ejecuta la aplicación tenga activado el inicio de sesión automático en el SO, y desactivado todos los bloqueos de pantalla y suspensión, para que una vez encendido el ordenador con el sistema, se muestre directamente el escritorio y arranque la aplicación core gracias al fichero .desktop.