# BUILD-USING:        docker build -t web-app .
# RUN-USING:          docker run -d -p 3000:3000 --mount source=storage,target=/app/storage web-app
FROM python:3.11.7-alpine3.19

VOLUME "/app/storage"

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY ./html ./html
COPY http_server.py  .
COPY main.py  .
COPY socket_server.py .

EXPOSE 3000

ENTRYPOINT ["python3", "/app/main.py"]
