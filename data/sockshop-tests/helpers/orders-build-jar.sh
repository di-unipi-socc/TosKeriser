#!/bin/sh
NAME=orders

abs_path=$(cd $(dirname $0) && pwd)

git clone  https://github.com/microservices-demo/$NAME.git $abs_path/$NAME

cd $abs_path/$NAME

mvn -DskipTests package

cp target/$NAME.jar $abs_path/../sockshop-app/artifacts && rm -rf $abs_path/$NAME
