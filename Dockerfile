FROM python:3.6-slim

WORKDIR /data

COPY . .

RUN apt-get update && \
    apt-get install python3-setuptools -y && \
    python3 setup.py install --install-scripts=/usr/bin

CMD nextcloud-news-updater --config config.ini
