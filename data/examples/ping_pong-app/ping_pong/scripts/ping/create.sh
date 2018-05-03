#!/bin/sh

tar -xf $INPUT_CODE && mv ping /ping

cd /ping && npm install
