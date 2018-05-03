#!/bin/sh

unset NODE_ENV

cd /ping && DEBUG=app:* node bin/www
