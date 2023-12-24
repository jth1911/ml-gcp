FROM tensorflow/tfx:1.8.0

WORKDIR /

COPY ./kfx /kfx
COPY ./.env /.env

COPY setup.py setup.py

RUN python setup.py install