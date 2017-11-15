#!/bin/sh

# # java -Djava.security.egd=file:/dev/urandom -jar /carts/target/carts.jar --port=$INPUT_PORT
# java -Djava.security.egd=file:/dev/urandom -jar $INPUT_JAR --port=$INPUT_PORT #-db=cart-db
export JAVA_OPTS=-Djava.security.egd=file:/dev/urandom

java -Ddebug -jar /orders/target/orders.jar --port=$INPUT_PORT

# java -jar $INPUT_JAR --port=$INPUT_PORT --shipping_endpoint=$INPUT_SHIPPING --payment_endpoint=$INPUT_PAYMENT
