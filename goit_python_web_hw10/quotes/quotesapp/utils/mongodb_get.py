from .models import Authors, Quotes
from mongoengine import connect


connect(host="mongodb+srv://goitlearn:V7zD6CSOSKUV1MHv@cluster0.vxz8fer.mongodb.net/hw09?retryWrites=true&w=majority&appName=Cluster0")


def authors():
    in_authors = Authors.objects.all()
    for author in in_authors:
        output = {
            "fullname": author.fullname,
            "born_date": author.born_date,
            "born_location": author.born_location,
            "description": author.description
        }
        yield output


def quotes():
    in_quotes = Quotes.objects.all()
    for quote in in_quotes:
        output = {
            "tags": [tag.name for tag in quote.tags],
            "author": quote.author.fullname,
            "quote": quote.quote
        }
        yield output
