# unclasified-archiver

**A shity script for organize mesh media data on my family storage.**

Hace mucho tiempo la vida era mas sencilla. Con mi novia y mi *n900*, podias almacenar en 10 Gb en la nube (Dropbox) las fotos y videos de varios años... pero ahora, despues de que mis hijas alcanzaran la edad adolescentil, el *Datagedon* ha llegado a mi hogar. Con 4 Tb de disco en la lan de casa espero que al menos tenga para un par de años... Por que llegara el dia que llenen de fotos maquillandose y 14 perspectivas del mismo selfie el disco que he predispuesto de 4TB... entonces tendremos que hacer un poco mas de lo mismo, comprar dos discos mas grande (uno para backup) y almacenar tan apreciada libreria grafica.

## Contexto

El problema nos surgio en un punto del año pasado y es que nos quedabamos sin espacio en google drive. Ya estaba pagando la cuota de 200 Gb de one drive y eso se llenaba en cuestion de semanas (en cuatro meses cada una de las cachorritas me generan 200 Gb). Durante algunos de los meses de principio de año, me descargue (google takeout) los archivos mas pesados de las nenas, pero aun asi eso se llenaba rapido (lo dicho, 200Gb en cuestion de semanas), así que me vi en la necesidad de o actualizar a 2 TB (100 €/año) o hacer algo para que pudieran tener sus medios. La forma que estaba utilizando para sincronizar fue utilizando synchthing (lo recomiendo encarecidamente, pero no tiene soporte para ios) y anteriormente sync (resilio sync, este lo deje de utilizar porque dejaba mi caca NAS demasiada petada la CPU).

Al principio, usando estos programas de syncronizacion en el storage familiar, volcaba todo el telefono de cada uno de los miembros familiares (que no fuera eso por lo que el Sync me dejaba frito el NAS... :P), pero al final entendi que esto es demasiado y que lo unico que me interesa almacenar son las carpetas de las fotos, cosa que empece ha hacer a posteriori... Mi forma de hacer el cambio de uno a otro movil (cuando se le rompia a alguien) era mover la carpeta de sync a otro lado y seguir como si nada, esto genero varias decenas de carpetas con miles de archivos y directorios cada uno de su padre y de su madre. Ya lo organizaran, pense, y como no lo hicieron, pues programe este script.

## Que hace

Te recorre un directorio de forma recursiva localizando todos los archivos y organizandolos en carpetas en base a la fecha de los mismos. A traves de configuracion estableces una entrada (formato ini) con una carpeta origen `unclasified_folder` y una carpeta destino `archive_folder`.

Si son archivos de medios visuales (videos e imagenes), los mete directamente en el directorio `archive_folder` en una carpeta con el año y otra hija con el mes del medio (priorizando exif y nombre de archivo), los archivos de audio, los mete en una carpeta `audio` dentro de `archive_folder` y el resto en una carpeta `other` dentro de la misma carpeta.

Si son archivos de medios visuales que no consigue obtener la fecha del medio a partir del exif o del nombre del archivo, los mete en una carpeta `modified-date` y calcula la fecha en base a la fecha de modificacion del archivo. Esto lo hace asi porque esa fecha no solo es poco fiable, sino que ademas muchas veces esta mal (es la fecha del momento que copiaste el archivo en el disco cuasi siempre)

Con todo esto hay veces que puede encontrar archivos duplicados en fecha y nombre, utilizando md5, comprueba si son identicos y si son identicos los elimina del origen (ya lo tienes en `archive_folder`, me parecio conveniente que se comportara por defecto asi, aunque tienes la opcion de copiar archivos en vez de moverlos en cuyo caso no lo eliminara), y si en caso de colision, no coincide con el md5, los mantiene en el directorio `unclasified_folder` sin tocarlo y saca un error mencionando este hecho que tendras que resolver manualmente.

## Enlaces relacionados

* https://docs.python.org/3/library/configparser.html
* https://docs.python.org/es/3/library/getopt.html
* https://github.com/kkroening/ffmpeg-python
* https://github.com/ahupp/python-magic
* https://github.com/sbraz/pymediainfo
* https://github.com/carsales/pyheif
* https://github.com/sashsinha/simple-file-checksum/


## Instalacion y ejecucion

Las dos opciones que propongo son estas:

* **Python local**, instalas python (si no lo tenias ya) y las dependencias, copias el script en algun sitio y listo. (OJO: por ahora la guia esta solo probada con ubuntu)
    * **(opcional) con pyenv**, para tener en un entorno aislado las dependencias de python
* **Imagen de Docker**, para mi la mejor opcion, ya que las dependencias son pesadas (1.4 Gb de img... es lo que tiene el ffmpeg) y algunas veces dolorosas de mantener

### Python local

1. Descargamos el codigo de este repo:
```bash
git clone https://github.com/moz667/unclasified-archiver.git unclasified-archiver
cd unclasified-archiver
```
2. Instalamos las dependencias:
```bash
sudo apt install python3 python3-pip ffmpeg libmediainfo0v5 openssl
pip3 install -r requirements.txt
```
3. Creamos un archivo de configuracion, por ejemplo creamos el archivo `config.ini`
4. Ejecutamos una prueba:
```bash
python3 src/unclasified-archiver.py --c=config.ini --dry-run
```
5. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
python3 -O src/unclasified-archiver.py --c=config.ini
```

#### Gestionando dependencias de python con pyenv

1. Descargamos el codigo de este repo:
```bash
git clone https://github.com/moz667/unclasified-archiver.git unclasified-archiver
cd unclasified-archiver
```
2. Instalamos algunas dependencias (NO python):
```bash
sudo apt install ffmpeg libmediainfo0v5 openssl
```
3. Instalamos y configuramos [pyenv](https://github.com/pyenv/pyen)
4. Creamos un entorno virtual para este script:
```bash
pyenv virtualenv 3.12.5 unclasified-archiver
echo "unclasified-archiver" > .python-version
```
5. Instalamos las dependencias de python (`requirements.txt`):
```bash
pip install -r requirements.txt
```
6. Creamos un archivo de configuracion, por ejemplo creamos el archivo [`config.ini`](#configuracion)
7. Ejecutamos una prueba:
```bash
python3 src/unclasified-archiver.py --c=config.ini --dry-run
```
8. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
python3 -O src/unclasified-archiver.py --c=config.ini
```

### Docker

1. Instalamos y configuramos [docker](https://docs.docker.com/engine/install/)
2. Creamos un archivo de configuracion, por ejemplo creamos el archivo [`config.ini`](#configuracion)
3. Ejecutamos una prueba:
```bash
cat config.ini | docker run -i --rm -v ~/unclasified_folder:/unclasified \
    -v ~/archive_folder:/archive moz667/unclasified-archiver \
    python ./unclasified-archiver.py --dry-run
```
4. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
cat config.ini | docker run -i --rm -v ~/unclasified_folder:/unclasified \
    -v ~/archive_folder:/archive moz667/unclasified-archiver
```

**OJO: Hay que tener en cuenta que para que el script acceda a la estructura de directorios del host donde se ejecuta, lo tenemos que montar como volumenes. Esto es importante entenderlo ya que por un lado en la ejecucion con docker hay que incluir los parametros `-v` indicando origen y destino del volumen para las distintas carpetas, y por otro lado en el archivo de configuracion tenemos que establecer las rutas dentro del contenedor (no las rutas de tu host)**

#### Me construyo mi propia imagen, con casinos... y fur...

1. Descargamos el codigo de este repo:
```bash
git clone https://github.com/moz667/unclasified-archiver.git unclasified-archiver
cd unclasified-archiver
```
2. Construimos la imagen:
```bash
docker build . --tag custom-unclasified-archiver
```
3. Creamos un archivo de configuracion, por ejemplo creamos el archivo [`config.ini`](#configuracion)
4. Ejecutamos una prueba:
```bash
cat config.ini | docker run -i --rm -v ~/unclasified_folder:/unclasified \
    -v ~/archive_folder:/archive custom-unclasified-archiver \
    python ./unclasified-archiver.py --dry-run
```
5. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
cat config.ini | docker run -i --rm -v ~/unclasified_folder:/unclasified \
    -v ~/archive_folder:/archive custom-unclasified-archiver
```

## Configuracion

La configuración se define con la estructura de un archivo ini (lo que lee [configparser](https://docs.python.org/3/library/configparser.html)) con al menos una seccion `[seccion-de-ejemplo]`.

Cada una de las secciones, define un proceso de archivado distinto, tener en cuenta que el script ejecutara secuncialmente procesos definidos en estas.

El nombre de las secciones es irrelevante, aunque recomendamos que sea algo que indetifique el proceso en si.

Dentro de cada seccion, estableceremos las distintas opciones del proceso de archivado. 

> **OJO:** Cada seccion debe definir al menos una carpeta origen `unclasified_folder` donde estan los archivos desordenados y una carpeta destino `archive_folder` en la que te generara una estructura de directorios y movera (o copiara) los archivos ya ordenados.

Las opciones dentro de la seccion son:

* `unclasified_folder` (cadena), la ruta a la carpeta origen (**obligatorio**)
* `archive_folder` (cadena), la ruta a la carpeta destino (**obligatorio**)
* `move_files` (valores true ó false), define si mueve los archivos desde `unclasified_folder` hasta la nueva estructura dentro de `archive_folder`, o si por el contrario, queremos copiar (**por defecto `true`, es decir, mueve los archivos**)
* `delete_empty_dir` (valores true ó false), define si al acabar de recorrer toda la estructura de la carpeta `unclasified_folder` elimina los directorios vacios (**por defecto `true`, es decir, elimina los directorios vacios del origen**)
* `ignore_no_media_files` (valores true ó false), ignora o no archivos considerados no media manteniendolos en el directorio de origen. (**por defecto `false`, es decir, que no los ignora y los mueve**)
* `resilio_trashed_files` (valores true ó false). Si esta opción es `true`, cambia el nombre del archivo de destino eliminando el prefijo `.trashed-0000000000-`-. Hay que tener en cuenta que siempre se mueven este tipo de archivos incluso si la opción `move_files` está establecida en `false`. (**por defecto `false`, es decir, no trata de forma distinta esos archivos**)
* `resilio_backup` (valores true ó false). Esta opcion marcada como `true`, es un atajo a otras opciones (ignorando el resto de ellas), establece:
    * `move_files=false`
    * `delete_empty_dir=false`
    * `ignore_no_media_files=true`
    * `resilio_trashed_files=true`

### Ejemplo de configuracion

```ini
[photos_mesh]
;`unclasified_folder` (cadena), la ruta a la carpeta origen (**obligatorio**)
unclasified_folder=Documents/photos-mesh

;`archive_folder` (cadena), la ruta a la carpeta destino (**obligatorio**)
archive_folder=Documents/Images/archive

;`move_files` (valores true ó false), define si mueve los archivos desde 
;       `unclasified_folder` hasta la nueva estructura dentro de `archive_folder`
;       , o si por el contrario, queremos copiar (**por defecto `true`, es decir, 
;       mueve los archivos**)

;`delete_empty_dir` (valores true ó false), define si al acabar de recorrer toda
;la estructura de la carpeta `unclasified_folder` elimina los directorios vacios
;(**por defecto `true`, es decir, elimina los directorios vacios del origen**)

;`ignore_no_media_files` (valores true ó false), ignora o no archivos 
;considerados no media manteniendolos en el directorio de origen. (**por defecto
;`false`, es decir, que no los ignora y los mueve**)

;`resilio_trashed_files` (valores true ó false). Si esta opción es `true`, 
;cambia el nombre del archivo de destino eliminando el prefijo 
;`.trashed-0000000000-`-. Hay que tener en cuenta que siempre se mueven este 
;tipo de archivos incluso si la opción `move_files` está establecida en `false`.
;(**por defecto `false`, es decir, no trata de forma distinta esos archivos**)

;`resilio_backup` (valores true ó false). Esta opcion marcada como `true`, es un
;atajo a otras opciones (ignorando el resto de ellas), establece:
;   * `move_files=false`
;   * `delete_empty_dir=false`
;   * `ignore_no_media_files=true`
;   * `resilio_trashed_files=true`

; tipica carpeta con el backup de fotos de un movil con Resilio Sync
[resilio_backup_photos]
unclasified_folder=Resilio Sync/Images Backup
archive_folder=Documents/Images/archive
resilio_backup=true

; Una carpeta compartida que no quieres mover archivos y quieres 
; ignorar archivos que no sean fotos, videos o audios
[public_folder_mesh]
unclasified_folder=shared
archive_folder=Documents/Images/archive
move_files=false
delete_empty_dir=false
ignore_no_media_files=true
```

## Argumentos del script

* `--c=<config.ini>, --config=<config.ini>` (**Obligatorio**), fichero de configuracion con las distintas secciones
* `--dry-run`, no modifica nada, solo saca por pantalla lo que haria si ejecutas sin el `--dry-run`
* `--help`, te saca una ayuda con estos parametros

## Argumentos de ejecucion de python

Por defecto, el script genera bastante texto de salida diciendo donde esta y que esta haciendo con tus archivos, para reducir este ruido hay que ejecutar el script con la opcion `-O`
By default, the script generates some verbose output, to reduce this, execute python with `-O` argument.

**De la ayuda `man python`:**

**-O** Remove  assert statements and any code conditional on the value of __debug__; augment the filename for compiled (bytecode) files by adding .opt-1 before the .pyc extension.

Ver tambien [`__debug__`](https://docs.python.org/3/library/constants.html#debug__)

## Ejemplos de ejecucion

```bash
# Prueba de ejecucion (con salida normal y con un config.ini en la ruta que lo 
# estes ejecutando)
python unclasified-archiver.py --dry-run

# Ejecuta con salida normal y con un config.ini en la ruta que lo 
# estes ejecutando)
python unclasified-archiver.py

# Ejecuta con salida normal y con un config.ini en una ruta determinada)
python unclasified-archiver.py --c=/etc/unclasified-archiver/config.ini

# Ejecuta con salida minima (solo errores) y con un config.ini en una ruta 
# determinada)
python -O unclasified-archiver.py --c=/etc/unclasified-archiver/config.ini
```
