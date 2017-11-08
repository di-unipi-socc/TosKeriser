#!/bin/bash
ARGS=1         # Script requires 3 arguments.
E_BADARGS=85   # Wrong number of arguments passed to script.
SECS=10;
now=$(date '+%d-%m-%Y_%H:%M:%S');
PATH_LOGS="./logs/${now}_tosker_memcpu.log"

if [ $# -ne "$ARGS" ]
then
  echo "Usage:  `basename $0` SOCKSHOP_YAML_FILE"
  exit $E_BADARGS
fi

SOCKSHOP_YAML=$1

tosker $SOCKSHOP_YAML create start

echo "Waiting ${SECS} seconds before running  docker stats command..."
sleep ${SECS}s
# add the stats into the logs about the CPU and memory used by all the container
docker stats --no-stream --format 'table {{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}' > "$PATH_LOGS"
echo "Mem/CPU stats written in file $PATH_LOGS"


now=$(date '+%d-%m-%Y_%H:%M:%S');
CSV_BASE_NAME="../logs/${now}_tosker"
cd test/ && ./runLocust.sh -h 127.0.0.1 -r 40s -c 100 -l ${CSV_BASE_NAME}

echo "Load stats written in file ${CSV_BASE_NAME}"

tosker $SOCKSHOP_YAML stop delete
