#!/bin/sh

tar -xf $INPUT_CODE && mv proxy /proxy


go get -u github.com/BurntSushi/toml

cd /proxy
mkdir -p ./bin
go build -i -o ./bin/proxy
