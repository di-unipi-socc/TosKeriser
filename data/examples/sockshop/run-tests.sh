#!/bin/bash
ARGS=1         # Script requires 3 arguments.
E_BADARGS=85   # Wrong number of arguments passed to script.

now=$(date '+%d-%m-%Y_%H:%M:%S');
PATH_LOGS="./logs/${now}_sockshop.log"
echo $PATH_LOGS

if [ $# -ne "$ARGS" ]
then
  echo "Usage:  `basename $0` SOCKSHOP_YAML_FILE"
  exit $E_BADARGS
fi

SOCKSHOP_YAML=$1

tosker $SOCKSHOP_YAML create start

# add the stat into the logs about the CPU and memory used by all the container
# watch -n
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' >> "$PATH_LOGS"

echo "Stats written in file $PATH_LOGS"
