#!/bin/sh


if [ $# -lt 2 ]
then
	echo "Please provide game id and player count"
	exit -1
fi

GAME_ID=$1
PLAYER_COUNT=$2

i=0
while [ $i -lt $PLAYER_COUNT ]
do
	python agent_init.py $GAME_ID &
	i=`expr $i + 1`
done

wait