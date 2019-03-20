#!/bin/sh

# very rudimentary startup scripts; long way to go

docker run --rm -d --name=crossbar -p 80:80 --network=monopolynetwork router
retval=$?

if test $retval != 0 ; then
    echo "Could not start the services:("
else
    docker run -d --rm --network=monopolynetwork game_generator
    retval=$?
    if test $retval != 0 ; then
        ./cleanup.sh
        echo "Could not start the services:("
    else
        docker run -d --rm --network=monopolynetwork adjudicator
    fi
fi


