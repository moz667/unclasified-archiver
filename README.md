# syncthing-archiver

Archivador de imagenes almacenadas en las carpetas de stdversions de synchthing

## Enlaces
* https://docs.python.org/3/library/configparser.html
* https://docs.python.org/es/3/library/getopt.html
* https://docs.python.org/3/library/hashlib.html
* https://exif.readthedocs.io/en/latest/usage.html
* https://github.com/kkroening/ffmpeg-python
* https://github.com/ahupp/python-magic
* https://github.com/sbraz/pymediainfo
* https://github.com/carsales/pyheif


## Environment (con pyenv)

```bash
pyenv virtualenv 3.7.2 syncthing-archiver
echo "syncthing-archiver" > .python-version
pip install --upgrade pip
pip install -r requirements.txt
```

## Estructura de directorios en el archivo

Si tiene fecha del meta o del nombre del archivo:

* Carpeta con el año
    * Carpeta con el mes

Si no tiene alguna de las fechas anteriores

* Carpeta `unclassified`
    * Carpeta con el año de creacion del archivo
        * Carpeta con el mes de creacion del archivo

## TODO
* [ ] Configuracion
* [ ] Archivos .trash (verificar por si se borro antes de sincronizar)
* [ ] Documentar como sincronizar
    * [ ] Android
    * [ ] IOS