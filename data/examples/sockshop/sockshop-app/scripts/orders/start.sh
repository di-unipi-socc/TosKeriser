#!/bin/sh

# # java -Djava.security.egd=file:/dev/urandom -jar /carts/target/carts.jar --port=$INPUT_PORT
# java -Djava.security.egd=file:/dev/urandom -jar $INPUT_JAR --port=$INPUT_PORT #-db=cart-db
export JAVA_OPTS=-Djava.security.egd=file:/dev/urandom

java -jar /orders/target/orders.jar --port=$INPUT_PORT
