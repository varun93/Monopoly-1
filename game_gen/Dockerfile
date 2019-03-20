FROM crossbario/autobahn-python:cpy3

RUN pip install --upgrade autobahn

WORKDIR /app
COPY . /app

ENV CBURL ws://crossbar:80/ws
ENV CBREALM realm1

# both these parameters are currenty hardcoded but they are will be application generated
# in future
CMD ["python", "game_gen.py", "1", "6"]
