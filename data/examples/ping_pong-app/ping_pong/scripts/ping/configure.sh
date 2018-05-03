#!/bin/sh

CONF=/ping/config/default.toml
echo "port = $INPUT_PORT" > $CONF
echo "proxy = \"$INPUT_PROXY\"" >> $CONF
