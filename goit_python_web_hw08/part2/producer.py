import json
from faker import Faker
import pika
from models import Contacts
import connect
from seed import seed


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )
)
channel = connection.channel()

channel.exchange_declare(exchange='notifications', exchange_type='direct')

channel.queue_declare(queue='email', durable=True)
channel.queue_bind(exchange='notifications', queue='email')

channel.queue_declare(queue='sms', durable=True)
channel.queue_bind(exchange='notifications', queue='sms')


def main():
    seed()

    contacts = Contacts.objects()
    print(contacts)
    for index, contact in enumerate(contacts):
        message = {
            "id": index + 1,
            "contact_id": str(contact.id),
            "message": Faker().text()
        }
        print(message)

        channel.basic_publish(
            exchange='notifications',
            routing_key=contact.preffered,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        print(" [x] Sent %r" % message)
    connection.close()


if __name__ == "__main__":
    main()
