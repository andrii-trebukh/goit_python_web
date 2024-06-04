FROM python:3.11.7-alpine3.19

ENV APP_HOME /app
ENV HOME $APP_HOME
WORKDIR $APP_HOME

COPY ./personal_assistant ./personal_assistant
COPY requirements.txt .

RUN mkdir ~/.personal_assistant/

COPY contact_book.bin $APP_HOME/.personal_assistant/contact_book.bin
COPY notes_book.bin $APP_HOME/.personal_assistant/notes_book.bin

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "./personal_assistant/main.py"]
