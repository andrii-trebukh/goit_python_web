#!/bin/sh

docker run -d --name redis-cache -p 6379:6379 redis
