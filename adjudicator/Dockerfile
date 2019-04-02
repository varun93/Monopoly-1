FROM crossbario/autobahn-python:cpy3

RUN pip install --upgrade autobahn

WORKDIR /app
COPY . /app

ENV CBURL ws://crossbar:80/ws
ENV CBREALM realm1


# docker run -v $PWD/adjudicator:/app -e CBURL="ws://crossbar:80/ws" -e CBREALM="realm1" --link=crossbar --rm -it crossbario/autobahn-python:cpy3 python /app/newAdjudicator.py
