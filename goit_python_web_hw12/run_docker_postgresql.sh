#!/bin/sh

docker run -d \
    --name rest_app \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=t3366XLOSoV8 \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v /home/sims/Projects/goit_python_web_hw12/postgresql_db:/var/lib/postgresql/data \
    postgres
