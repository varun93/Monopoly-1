#!/bin/sh

docker create network monopolynetwork

docker build --tag=router:latest router
docker build --tag=game_generator:latest game_gen
docker build --tag=adjudicator:latest adjudicator