FROM crossbario/autobahn-python:cpy3

RUN pip install --upgrade autobahn

WORKDIR /app
COPY . /app

ENV CBURL ws://crossbar:3000/ws
ENV CBREALM realm1

ENTRYPOINT ./wait-for-it.sh crossbar:3000 -t 120 -- crossbar start



