#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately

ARGS=1         # Script requires 3 arguments.
E_BADARGS=85   # Wrong number of arguments passed to script.
SECS=40;
now=$(date '+%d-%m-%Y_%H:%M:%S');
PATH_LOGS="./logs/${now}_compose_memcpu.log"

if [ $# -ne "$ARGS" ]
then
  echo "Usage:  `basename $0` DOCKER_COMPOSE_FILE"
  exit $E_BADARGS
fi

DOCKER_COMPOSE_FILE=$1
echo $DOCKER_COMPOSE_FILE
docker-compose -f $DOCKER_COMPOSE_FILE up -d

echo "Waiting ${SECS} seconds before running  docker stats command..."
sleep ${SECS}s
# add the stats into the logs about the CPU and memory used by all the container
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' > "$PATH_LOGS"
echo "Mem/CPU stats written in file $PATH_LOGS"


now=$(date '+%d-%m-%Y_%H:%M:%S');
CSV_BASE_NAME="../logs/${now}_compose"
cd test/ && ./runLocust.sh -h 127.0.0.1 -r 1m -c 1000 -l ${CSV_BASE_NAME}

echo "Load stats written in file ${CSV_BASE_NAME}"

docker-compose -f $DOCKER_COMPOSE_FILE down
