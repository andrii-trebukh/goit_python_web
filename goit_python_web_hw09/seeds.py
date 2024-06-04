from datetime import datetime
import json
from models import Tag, Authors, Quotes
import connect


def main():
    with open("authors.json", "r", encoding="utf-8") as fh:
        authors = json.load(fh)

    Authors().drop_collection()
    for author in authors:
        Authors(
            fullname=author["fullname"],
            born_date=datetime.strptime(author["born_date"], "%B %d, %Y"),
            born_location=author["born_location"],
            description=author["description"]
        ).save()

    with open("qoutes.json", "r", encoding="utf-8") as fh:
        quotes = json.load(fh)

    Quotes().drop_collection()
    for quote in quotes:
        author = Authors.objects(fullname=quote["author"])

        tags = [Tag(name=tag) for tag in quote["tags"]]

        Quotes(
            tags=tags,
            author=author[0],
            quote=quote["quote"]
        ).save()


if __name__ == "__main__":
    main()
