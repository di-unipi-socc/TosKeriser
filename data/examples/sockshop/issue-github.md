## Configurations of the microservices

A microservice-based system should allow to easily change the configuration of the microservices [Eberhard Wolff](https://www.amazon.com/Microservices-Flexible-Architecture-Eberhard-Wolff/dp/0134602412) :sunglasses:.


Currently, `SockShop` application is not equipped with a configuration mechanism but the configurations of the microservices are hardcoded :sob:.

For example, the endpoints in the `front-end`  reads the [`endpoint.js`](https://github.com/microservices-demo/front-end/blob/master/api/endpoints.js) file for knowing the endpoints of all the other microservices in the architecture.
With this implementation, I cannot configure the `hostname` and/or the `port` of the microservices.

```
module.exports = {
    catalogueUrl:  util.format("http://catalogue%s", domain),
    tagsUrl:       util.format("http://catalogue%s/tags", domain),
    cartsUrl:      util.format("http://carts%s/carts", domain),
    ordersUrl:     util.format("http://orders%s", domain),
    customersUrl:  util.format("http://user%s/customers", domain),
    addressUrl:    util.format("http://user%s/addresses", domain),
    cardsUrl:      util.format("http://user%s/cards", domain),
    loginUrl:      util.format("http://user%s/login", domain),
    registerUrl:   util.format("http://user%s/register", domain),
  };
  ```


I was wondering if Sockshop can be equipped with a configuration mechanism where each microservice can be configured independently.

The following solutions can be adopted:
 1. Include each microservices with a configuration file (where `hostname`, `port`,`db_connection`, etc... can be specified).
 2. Use a configuration server like the following ones
    -  [Spring Cloud config](https://cloud.spring.io/spring-cloud-config/) provides a resource-based API for external configuration.
   -  [Zookeeper](https://zookeeper.apache.org/)

Thank you in advance.
