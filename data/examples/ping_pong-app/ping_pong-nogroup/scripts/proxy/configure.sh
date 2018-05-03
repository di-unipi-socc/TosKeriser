#!/bin/sh

CONF=/proxy/conf.toml
echo "Port = $INPUT_PORT" > $CONF
echo "NextURL = \"$INPUT_PONG\"" >> $CONF
