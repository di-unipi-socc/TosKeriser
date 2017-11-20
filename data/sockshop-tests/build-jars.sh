#!/bin/bash
abs_path=$(cd $(dirname $0) && pwd)

# Builds the  jar file of the  "carts", "orders" and  "shipping" microservices..

echo "Creating carts into /artifacts folder (carts.jar) ..."
$abs_path/helpers/carts-build-jar.sh &> /dev/null

echo "Creating orders  into /artifacts folder (orders.jar) ..."
$abs_path/helpers/orders-build-jar.sh &> /dev/null

echo "Creating shipping  into /artifacts folder (shipping.jar) ..."
$abs_path/helpers/shipping-build-jar.sh &> /dev/null
