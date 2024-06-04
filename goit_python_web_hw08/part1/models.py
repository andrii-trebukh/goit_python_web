from mongoengine import EmbeddedDocument, Document
from mongoengine.fields import DateTimeField, EmbeddedDocumentField, \
    ListField, StringField, ReferenceField


class Tag(EmbeddedDocument):
    name = StringField()


class Authors(Document):
    fullname = StringField()
    born_date = DateTimeField()
    born_location = StringField()
    description = StringField()


class Quotes(Document):
    tags = ListField(EmbeddedDocumentField(Tag))
    author = ReferenceField(
        Authors,
        dbref="ObjectId",
        reverse_delete_rule=2)
    quote = StringField()
