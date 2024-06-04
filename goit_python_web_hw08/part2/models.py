from mongoengine import Document
from mongoengine.fields import StringField, BooleanField, EmailField


class Contacts(Document):
    fullname = StringField()
    email = EmailField()
    sent = BooleanField()
    phone = StringField()
    preffered = StringField(regex="sms|email")
