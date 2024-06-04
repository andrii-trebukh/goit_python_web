import pika
import time
import json
from models import Contacts
import connect


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )
)
channel = connection.channel()

channel.queue_declare(queue='email', durable=True)
print('Waiting for messages. To exit press CTRL+C')


def send_email(contact_name, email, message):
    print(
        f"Sending email to contact {contact_name}"
        f": email: {email}, message: {message}"
    )
    time.sleep(1)
    print("email sent")


def callback(ch, method, properties, body):
    message = json.loads(body.decode())
    contact = Contacts.objects(id=message["contact_id"])[0]
    send_email(
        contact.fullname,
        contact.email,
        message["message"]
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    contact.update(sent=True)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='email', on_message_callback=callback)


if __name__ == '__main__':
    channel.start_consuming()
