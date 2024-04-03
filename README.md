# syncthing-archiver

Archivador de imagenes almacenadas en las carpetas de stdversions de synchthing

## Enlaces
* https://docs.python.org/es/3/library/getopt.html
* https://docs.python.org/3/library/configparser.html
* https://pypi.org/project/pillow/

## Environment (con pyenv)

```bash
pyenv virtualenv 3.7.2 syncthing-archiver
echo "syncthing-archiver" > .python-version
pip install --upgrade pip
pip install -r requirements.txt
```

## TODO
* [ ] Configuracion
* [ ] Archivos .trash (verificar por si se borro antes de sincronizar)
* [ ] Sqlite con info? Lo mismo puede ser interesante almacenar de alguna forma los sha1 de los archivos para validar duplicados o borrados (.trash)
* [ ] Documentar como sincronizar
    * [ ] Android
    * [ ] IOS