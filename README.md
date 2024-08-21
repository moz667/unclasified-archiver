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

## Instalacion

Por ahora hay que instalarlo a manija, aqui os relato la instalacion que hice con mi NAS (Ubuntu 22.04)

```bash
sudo apt install ffmpeg libmediainfo0v5 openssl
cd src
pip3 install -r requirements.txt
```

## Ejemplo de config

```ini
[folder1_to_archive]
; unclasified_folder (required), source folder with messy files and directories
; to trasverse
unclasified_folder=folder1/unclasified
; archive_folder (required), target folder to create the archive estructure
archive_folder=folder1
; move_files, true by default, move files from unclasified_folder to the new
; estructure if true, else copy
; move_files=true
; delete_empty_dir, true by default, delete empty dirs inside unclasified_folder 
; after move to archive_folder
; delete_empty_dir=true

[folder2_to_archive]
unclasified_folder=folder2/unclasified
archive_folder=folder2

[folderX_to_archive]
unclasified_folder=folderX/unclasified
archive_folder=folderX
```

## Argumentos del script

* `-c <config.ini>, --config=<config.ini>` (**Obligatorio**), fichero de configuracion con las distintas secciones
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
python unclasified-archiver.py -c /etc/unclasified-archiver/config.ini

# Ejecuta con salida minima (solo errores) y con un config.ini en una ruta 
# determinada)
python -O unclasified-archiver.py -c /etc/unclasified-archiver/config.ini
```

## Related links
* https://docs.python.org/3/library/configparser.html
* https://docs.python.org/es/3/library/getopt.html
* https://github.com/kkroening/ffmpeg-python
* https://github.com/ahupp/python-magic
* https://github.com/sbraz/pymediainfo
* https://github.com/carsales/pyheif
* https://github.com/sashsinha/simple-file-checksum/

## Environment (con pyenv)

```bash
pyenv virtualenv 3.7.2 unclasified-archiver
echo "unclasified-archiver" > .python-version
pip install --upgrade pip
pip install -r requirements.txt
# Extra libs
apt install ffmpeg libmediainfo0v5 openssl
```

## TODO
* [ ] Dockerfile (too many soft reqs.)
