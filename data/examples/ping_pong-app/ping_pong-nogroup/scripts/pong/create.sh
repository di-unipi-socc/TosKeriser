#!/bin/sh

tar -xf $INPUT_CODE && mv pong /pong

cd /pong && pip install -r requirements.txt
