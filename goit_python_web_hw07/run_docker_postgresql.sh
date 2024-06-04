#!/bin/sh

docker run -d \
    --name some-postgres \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=eUSeCteRICtubeNA \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v /home/sims/Projects/goit_python_web_hw07/postgresql_db:/var/lib/postgresql/data \
    postgres