from random import randint, choice
from faker import Faker
from models import Contacts
import connect


CONTACTS_QUANTITY = 20


def seed():
    fake = Faker()
    Contacts.drop_collection()
    for _ in range(CONTACTS_QUANTITY):
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}" \
            f"@example.{choice(('com', 'net', 'org', 'gov'))}" \
            .replace("..", ".")
        Contacts(
            fullname=name,
            email=email,
            sent=False,
            phone="".join(str(randint(1, 9)) for _ in range(10)),
            preffered=choice(("sms", "email"))
        ).save()


if __name__ == "__main__":
    seed()
