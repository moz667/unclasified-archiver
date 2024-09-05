FROM python:3.12.5

RUN apt-get update && \
    apt-get -y --no-install-recommends install ffmpeg libmediainfo0v5 openssl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

RUN mkdir /opt/app

WORKDIR /opt/app

COPY src /opt/app
ADD requirements.txt /opt/app/
COPY config.sample.ini config.ini

RUN pip install -r requirements.txt

VOLUME /unclasified
VOLUME /archive

ENTRYPOINT []
CMD [ "python", "-O", "./unclasified-archiver.py", "--dry-run"]