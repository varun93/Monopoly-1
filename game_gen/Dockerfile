FROM crossbario/autobahn-python:cpy3

RUN pip install --upgrade autobahn

WORKDIR /app
COPY . /app

ENV CBURL ws://crossbar:80/ws
ENV CBREALM realm1
