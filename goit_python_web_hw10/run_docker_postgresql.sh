#!/bin/sh

docker run -d \
    --name quotes-postgres \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=bGVwY71aWs6CSFnq \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v /home/sims/Projects/goit_python_web_hw10/postgresql_db:/var/lib/postgresql/data \
    postgres