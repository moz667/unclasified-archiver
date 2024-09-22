# unclasified-archiver

**A shity script for organize mesh media data on my family storage.**

## Enlaces relacionados

* **Software relacionado (en mi caso)**
  * https://immich.app/
  * https://www.resilio.com/sync/
* **Librerias utilizadas**
  * https://docs.python.org/3/library/configparser.html
  * https://docs.python.org/es/3/library/getopt.html
  * https://docs.python.org/es/3/library/shelve.html
  * https://github.com/kkroening/ffmpeg-python
  * https://github.com/ahupp/python-magic
  * https://github.com/sbraz/pymediainfo
  * https://github.com/carsales/pyheif
  * https://github.com/sashsinha/simple-file-checksum/

## Contexto

**Antes de nada... un poquito de historia:**

> Hace mucho tiempo la vida era mas sencilla. Con mi novia y mi *n900*, podias almacenar en 10 Gb en la nube (Dropbox) las fotos y videos de varios años... pero ahora, despues de que mis hijas alcanzaran la edad adolescentil, el *Datagedon* ha llegado a mi hogar. Con 4 Tb de disco en la lan de casa espero que al menos tenga para un par de años... Por que llegara el dia que llenen de fotos maquillandose y 14 perspectivas del mismo selfie el disco que he predispuesto de 4TB... entonces tendremos que hacer un poco mas de lo mismo, comprar dos discos mas grande (uno para backup) y almacenar tan apreciada libreria grafica.

El problema nos surgio en un punto del año pasado y es que nos quedabamos sin espacio en google drive. Ya estaba pagando la cuota de 200 Gb de one drive y eso se llenaba en cuestion de semanas (en cuatro meses cada una de las cachorritas me generan 200 Gb). Durante algunos de los meses de principio de año, me descargue (google takeout) los archivos mas pesados de las nenas y los borre del espacio de google, pero aun asi eso se llenaba rapido (lo dicho, 200Gb en cuestion de semanas), así que me vi en la necesidad de o actualizar a 2 TB (100 €/año) o hacer algo para que pudieran tener sus medios. La forma que estaba utilizando para sincronizar fue utilizando synchthing (lo recomiendo encarecidamente, pero no tiene soporte para ios) y anteriormente sync (resilio sync, este lo deje de utilizar porque dejaba mi caca NAS demasiada petada la CPU).

Al principio, usando estos programas de syncronizacion en el storage familiar, volcaba todo el telefono de cada uno de los miembros familiares (que no fuera eso por lo que el Sync me dejaba frito el NAS... :P), pero al final entendi que esto es demasiado y que lo unico que me interesa almacenar son las carpetas de las fotos, cosa que empece ha hacer a posteriori... Mi forma de hacer el cambio de uno a otro movil (cuando se le rompia a alguien) era mover la carpeta de sync a otro lado y seguir como si nada, esto genero varias decenas de carpetas con miles de archivos y directorios cada uno de su padre y de su madre. Ya lo organizaran, pense... y como no lo hicieron, pues programe este script.

## Que hace

Te recorre un directorio de forma recursiva localizando todos los archivos y organizandolos en carpetas en base a la fecha de los mismos. A traves de configuracion estableces una entrada (formato ini) con una carpeta origen `unclasified_folder` y una carpeta destino `archive_folder`.

Si son archivos de medios visuales (videos e imagenes), los mete directamente en el directorio `archive_folder` en una carpeta con el año y otra hija con el mes del medio (priorizando exif y nombre de archivo), los archivos de audio, los mete en una carpeta `audio` dentro de `archive_folder` y el resto en una carpeta `other` dentro de la misma carpeta.

Si son archivos de medios visuales que no consigue obtener la fecha del medio a partir del exif o del nombre del archivo, los mete en una carpeta `modified-date` y calcula la fecha en base a la fecha de modificacion del archivo. Esto lo hace asi porque esa fecha no solo es poco fiable, sino que ademas muchas veces esta mal (es la fecha del momento que copiaste por primera vez el archivo en el disco cuasi siempre, cosa que me ocurre al sincronizar archivos de movil al servidor con resilio)

Con todo esto hay veces que puede encontrar archivos duplicados en fecha y nombre, utilizando md5, comprueba si son identicos y si son identicos los elimina del origen (ya lo tienes en `archive_folder`, me parecio conveniente que se comportara por defecto asi, aunque tienes la opcion de copiar archivos en vez de moverlos en cuyo caso no lo eliminara), y si en caso de colision, no coincide con el md5, los mantiene en el directorio `unclasified_folder` sin tocarlo y saca un error mencionando este hecho que tendras que resolver manualmente.

### Estado de copia (`copy_status.shelve`)

<!-- TODO: Hacer configurable esta opcion, aunque si bien con eliminar el archivo ya no es necesaria, es posible que algunos comportamientos se puedan evitar haciendo mas rapido el proceso de copia -->
<!-- TODO: El problema del moz del futuro... `copy_status.shelve` muy grandes -->

**Contexto:** Cuando estaba gestionando la copia de archivos de media generados con los moviles, me di cuenta que muchas veces te va a interesar borrar algunas de esas fotos de la galeria, el problema es que cuando lanzes de nuevo la sincronizacion, te va a volver a copiar estos archivos... ¿como podriamos evitar esto?. Pues lo primero que se me ocurrio fue utilizar un archivo temporal donde se almacene el estado de los archivos copiados (si ya se han copiado ya) y para ello buscando acerca de persistencia de objetos encontre [shelve](https://docs.python.org/es/3/library/shelve.html).

Antes de copiar o eliminar archivos (en el caso de mover) comprueba si ya se copio el archivo y de ser asi no lo vuelve a copiar  inclusive si no existe en el destino (o eliminar inclusive si ya existe en el destino).

Para hacer esto: **SOLO** cuando copia un archivo, se establece en un fichero (`copy_status.shelve`) que ha copiado este archivo añade un registro a la lista con una clave que es el checksum del archivo (`md5sum`) y el tamaño del mismo. La eleccion de esta estrategia para evitar posibles colisiones con los archivos es que en el escenario que tenemos (la media familiar) que ocurran 2 colisiones con estos dos es `'muy ' * 12` improbable.

Los archivos donde se almacena el estado se crean por defecto en el directorio `/tmp` del sistema donde se ejecute el script, pero este es configurable por otra ruta que queramos usar en la variable de entorno `COPY_STATUS_DIR`. En la version de docker, este directorio cambia a `/copy_status` (utilizando la variable de entorno antes mencionada) para poder crear un volumen si queremos almacenar el estado para futuras copias. **Esto hay que tenermo muy presente porque por defecto, se crean archivos volatiles que desapareceran en algun momento.**

Si por algun motivo, necesitamos volver a recrear el archivo de estado de la copia (), podemos establecer la opcion de configuracion `force_add2status=true`, que lo que hace basicamente es forzar aunque ya exista el archivo al realizar la tarea de archivado, guardar archivos anteriormente copiados el estado como copiado.

### Colisiones

Para gestionar las colisiones (y entendamos colisiones como archivos con el mismo nombre pero diferente `checksum` que se copian en el mismo destino), se tratan como una version alternativa del original, por ello cuando va a copiar (o mover) un archivo que colisiona en el destino, lo que hace es cambiarle el nombre incluyendo el sufijo `(Collision <checksum>)`, para asi asegurarse que no colisione en un futuro con este.

Al hacer la copia, el script, validara las dos posibilidades del archivo destino para elegir cual se eligio con anterioridad, es decir, copia o mueve siempre con el mismo nombre al destino.

### Ejemplos

#### Ejemplo 1: Manteniendo el estado entre copias

Plantemos el siguiente escenario con estos archivos:

* 1 con checksum A: 1(A)
* 1 con checksum B: 1(B)
* 2 con checksum C: 2(C)
* 3 con checksum A: 3(A)

| Origen(MD5)  | Destino(MD5)  | 
|--------------|---------------|
| 1(A)         |               |
| 1(B)         |               |
| 2(C)         |               |
| 3(A)         |               |

Cuando hagamos la copia, como 1 coincide con el nombre, pero tiene distinto checksum, añadiendo el sufijo de `(Collision B)` para que se mantenga en el nuevo. Por otra parte 3(A), como ya ha sido copiado, aunque tenga el nombre distinto, no lo copia. Esto se quedara asi mientras que no cambie nada y siempre que mantengamos el estado de la copia.

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
| 1(A)         | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         |                   |

Si borramos del origen el fichero 1(A), cuando va a copiar 1(B) detecta que se copio en 1(Collision B)(B) por lo que no copia y en destino sigue igual:

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
|              | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         |                   |

Si añadimos a origen un nuevo archivo con el mismo nombre 1(D), detecta las otras copias y copia en 1(Collision D)(D)

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
|              | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         |                   |
| 1(D)         | 1(Collision D)(D) |

Si eliminamos del destino 1(A), al copiar un nuevo archivo con el mismo nombre 1(E), pero distinto checksum y, al estar libre el nombre del archivo, lo copia en este

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
|              | 1(E)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 1(D)         | 1(Collision D)(D) |
| 3(A)         |                   |
| 1(E)         |                   |

#### Ejemplo 2: Sin mantener el estado entre copias

**Resumen: Es resultado es identico al Ejemplo 1, pero al no guardar estado, el archivo `3(A)` se trata de forma distinta**

Plantemos el siguiente escenario con estos archivos:

* 1 con checksum A: 1(A)
* 1 con checksum B: 1(B)
* 2 con checksum C: 2(C)
* 3 con checksum A: 3(A)

| Origen(MD5) | Destino(MD5) | 
|-------------|--------------|
| 1(A)        |              |
| 1(B)        |              |
| 2(C)        |              |
| 3(A)        |              |

Cuando hagamos la primera copia, como 1 coincide con el nombre, pero tiene distinto checksum, añadiendo el sufijo de `(Collision B)` para que se mantenga en el nuevo. Por otra parte 3(A), como ya ha sido copiado en esta iteracion, aunque tenga el nombre distinto, no lo copia.

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
| 1(A)         | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         |                   |

En una segunda copia, todo quedaria igual salvo que 3(A), como no coincide con el nombre y, aunque tenga el mismo checksum, copiara el archivo igualmente. Ya en sucesivas copias no cambiara nada.

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
| 1(A)         | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         | 3(A)              |

Si borramos del origen el fichero 1(A), cuando va a copiar 1(B) detecta que se copio en 1(Collision B)(B) por lo que no copia y en destino sigue igual:

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
|              | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         | 3(A)              |

Si añadimos a origen un nuevo archivo con el mismo nombre 1(D), detecta las otras copias y copia en 1(Collision D)(D)

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
|              | 1(A)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 3(A)         | 3(A)              |
| 1(D)         | 1(Collision D)(D) |

Si eliminamos del destino 1(A), al copiar un nuevo archivo con el mismo nombre 1(E), pero distinto checksum y, al estar libre el nombre del archivo, lo copia en este

| Origen(MD5)  | Destino(MD5)      | 
|--------------|-------------------|
|              | 1(E)              |
| 1(B)         | 1(Collision B)(B) |
| 2(C)         | 2(C)              |
| 1(D)         | 1(Collision D)(D) |
| 3(A)         | 3(A)              |
| 1(E)         |                   |

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

1. Instalamos algunas dependencias (NO python):
```bash
sudo apt install ffmpeg libmediainfo0v5 openssl
```
2. Instalamos y configuramos [pyenv](https://github.com/pyenv/pyen)
3. Creamos un entorno virtual para este script:
```bash
pyenv virtualenv 3.12.2 unclasified-archiver
echo "unclasified-archiver" > .python-version
```
4. Instalamos las dependencias de python (`requirements.txt`):
```bash
pip install -r requirements.txt
```
5. Creamos un archivo de configuracion, por ejemplo creamos el archivo [`config.ini`](#configuracion)
6. Ejecutamos una prueba:
```bash
python src/unclasified-archiver.py --c=config.ini --dry-run
```
7. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
python -O src/unclasified-archiver.py --c=config.ini
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

1. Construimos la imagen:
```bash
docker build . --tag custom-unclasified-archiver
```
2. Creamos un archivo de configuracion, por ejemplo creamos el archivo [`config.ini`](#configuracion)
3. Ejecutamos una prueba:
```bash
cat config.ini | docker run -i --rm -v ~/unclasified_folder:/unclasified \
    -v ~/archive_folder:/archive custom-unclasified-archiver \
    python ./unclasified-archiver.py --dry-run
```
4. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
cat config.ini | docker run -i --rm -v ~/unclasified_folder:/unclasified \
    -v ~/archive_folder:/archive custom-unclasified-archiver
```

#### Docker compose

He documentado esta opcion (que en mi caso es la que estoy utilizando) para poder simplificar un poco la gestion de los distintos archivados que quieras utilizar.

Utilizando el actual [docker-compose.yml](./docker-compose.yml) de este repo la instalacion y primera ejecucion seria:

1. Construimos la imagen:
```bash
docker compose build
```
3. Ejecucion de prueba:
```bash
docker compose run --rm test-files python ./unclasified-archiver.py --dry-run
```
1. Si lo vemos todo correcto (y no hay ninguna excepción) podemos ejecutar la version sin detalle de salida y ya modificando la estructura de archivos:
```bash
docker compose run --rm test-files
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
* `force_add2status` (valores true ó false), fuerza establecer el estado de la copia de archivos ya existentes en el destino (**por defecto `false`, es decir, que no fuerza el establecer el estado de archivos ya existentes**).
* `resilio_backup` (valores true ó false). Esta opcion marcada como `true`, es un atajo a otras opciones (ignorando el resto de ellas), establece:
    * `move_files=false`
    * `delete_empty_dir=false`
    * `ignore_no_media_files=true`
    * (**por defecto `false`, es decir, no trata de forma distinta esos archivos**)

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

;`resilio_backup` (valores true ó false). Esta opcion marcada como `true`, es un
;atajo a otras opciones (ignorando el resto de ellas), establece:
;   * `move_files=false`
;   * `delete_empty_dir=false`
;   * `ignore_no_media_files=true`
;(**por defecto `false`, es decir, no aplica la configuracion al proceso**)

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

## Ejemplo: Mi compose familiar

En mi caso, tengo un mini-servidor con un immich para gestionar los medios familiares. Si bien seguro que hay muchas otras formas de gestionar todo este batiburrillo de archivos, despues de varios años yo preferi hacer esta solucion (No me juzgueis).

El contexto (los nombres de usuarios y rutas son inventados):

* Los distintos moviles familiares se sincronizan al servidor a carpetas privadas cada uno con permisos solo para su usuario:
    * papa: /opt/resilio/papa
    * mama: /opt/resilio/mama
    * hija1: /opt/resilio/hija1
    * hija2: /opt/resilio/hija2
* Todos tenemos android salvo `hija2` que tiene ios (lo cual nos limita a actualizar solo las imagenes y videos capturados con el movil, mas informacion acerca del porque en este [articulo](https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities))
    * Los android hacen backup con resilio de las carpetas:
        * /opt/resilio/{usuario}/DCIM
        * /opt/resilio/{usuario}/Movies
        * /opt/resilio/{usuario}/Pictures
    * El ios hace backup con resilio de las imagenes y videos tomados con las camaras del telefono:
        * /opt/resilio/hija2/DCIM
* Cada usuario tiene su libreria externa de immich:
    * papa: /opt/immich/papa
    * mama: /opt/immich/mama
    * hija1: /opt/immich/hija1
    * hija2: /opt/immich/hija2

Asi que...

**1. He creado 2 archivos ini, uno para ios y otro para android:**
* `config.android.ini`
```ini
[DCIM]
unclasified_folder=/DCIM
archive_folder=/archive
resilio_backup=true
#force_add2status=true

[Movies]
unclasified_folder=/Movies
archive_folder=/archive
resilio_backup=true
#force_add2status=true

[Pictures]
unclasified_folder=/Pictures
archive_folder=/archive
resilio_backup=true
#force_add2status=true
```
* `config.ios.ini`
```ini
[DCIM]
unclasified_folder=/DCIM
archive_folder=/archive
resilio_backup=true
#force_add2status=true
```

**2. He definido un compose mapeando los volumenes con las distintas carpetas de usuarios:**

`docker-compose.yml`
```yml
services:
  papa-movil:
    image: moz667/unclasified-archiver:latest
    restart: "no"
    user: "1000"
    volumes:
      - ./config.android.ini:/opt/app/config.ini
      - /opt/papa/copy_status:/copy_status
      - /opt/immich/papa:/archive
      - /opt/resilio/papa/DCIM:/DCIM
      - /opt/resilio/papa/Movies:/Movies
      - /opt/resilio/papa/Pictures:/Pictures
  mama-movil:
    image: moz667/unclasified-archiver:latest
    restart: "no"
    user: "1001"
    volumes:
      - ./config.android.ini:/opt/app/config.ini
      - /opt/mama/copy_status:/copy_status
      - /opt/immich/mama:/archive
      - /opt/resilio/mama/DCIM:/DCIM
      - /opt/resilio/mama/Movies:/Movies
      - /opt/resilio/mama/Pictures:/Pictures
  hija1-movil:
    image: moz667/unclasified-archiver:latest
    restart: "no"
    user: "1002"
    volumes:
      - ./config.android.ini:/opt/app/config.ini
      - /opt/hija1/copy_status:/copy_status
      - /opt/immich/hija1:/archive
      - /opt/resilio/hija1/DCIM:/DCIM
      - /opt/resilio/hija1/Movies:/Movies
      - /opt/resilio/hija1/Pictures:/Pictures
  hija2-movil:
    image: moz667/unclasified-archiver:latest
    restart: "no"
    user: "1003"
    volumes:
      - ./config.ios.ini:/opt/app/config.ini
      - /opt/hija2/copy_status:/copy_status
      - /opt/immich/hija2:/archive
      - /opt/resilio/hija2/DCIM:/DCIM
```

**3. He creado un script que ejecuta todas las sincros:**

`archive-all.sh`
```bash
#!/bin/bash

echo "* Ejecutando papa..."
time docker compose run --rm papa-movil
echo "* Ejecutando mama..."
time docker compose run --rm mama-movil
echo "* Ejecutando hija1..."
time docker compose run --rm hija1-movil
echo "* Ejecutando hija2..."
time docker compose run --rm hija2-movil
```

Ahora ejecutando `archive-all.sh` tenemos todos los medios de los moviles familiares en cada una de sus librerias.

## Mesh

### Unittests

**Lanzar tests:**
```bash
python -O -m unittest tests.TestUnclasifiedArchive
```