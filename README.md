# unclasified-archiver

Archivador de imagenes almacenadas en las carpetas de stdversions de synchthing

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
apt install ffmpeg libmediainfo0v5
```

## TODO
* [ ] Complete document
* [ ] Dockerfile (too many soft reqs.)
