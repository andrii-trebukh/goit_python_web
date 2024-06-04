import redis
from redis_lru import RedisLRU
from models import Authors, Quotes
import connect


COMMANDS = {}
EXIT_FLAG = False

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


def usage():
    return "usage: {name,tag,tags}:[search string or list separated by comma]"


def make_nice_quotes(quotes: list):
    output = []
    for quote in quotes:
        output.append(
            f"id: {quote.id}\n"
            f"author: {quote.author.fullname}\n"
            f"tags: {', '.join(tag.name for tag in quote.tags)}\n"
            f"quote: {quote.quote}\n"
        )
    return "\n".join(output)


def command_handler(command):
    def outer_func(func):
        def wrapper(*args):
            return func(*args)

        COMMANDS[command] = wrapper

        return wrapper
    return outer_func


@command_handler("help")
def help_command(*_):
    return usage()


@command_handler("exit")
def exit_command(*_):
    global EXIT_FLAG
    EXIT_FLAG = True
    return "Bye"


@cache
def query_authors_by_name(keyword):
    return Authors.objects(fullname__icontains=keyword)


@cache
def query_quotes_by_author(keyword):
    return Quotes.objects(author=keyword)


@cache
def query_quotes_by_tag(keyword):
    return Quotes.objects(tags__name__icontains=keyword)


@command_handler("name")
def name(*args):
    if args[0] == "":
        return "Search string is empty"
    quotes = []
    authors = query_authors_by_name(args[0])
    for author in authors:
        quotes.extend(query_quotes_by_author(author))
    if quotes:
        return make_nice_quotes(quotes)
    return "Nothing found"


@command_handler("tag")
def tag(*args):
    if args[0] == "":
        return "Search string is empty"
    quotes = query_quotes_by_tag(args[0])
    if quotes:
        return make_nice_quotes(quotes)
    return "Nothing found"


@command_handler("tags")
def tags(*args):
    if args[0] == "":
        return "Search string is empty"
    quotes = []
    for arg in args:
        quotes.extend(query_quotes_by_tag(arg))
    if quotes:
        return make_nice_quotes(quotes)
    return "Nothing found"


def main():
    print(usage())
    while not EXIT_FLAG:
        input_string = input(">>> ")
        input_string = input_string.strip().split(":")
        input_command = input_string.pop(0).strip()
        if input_string:
            input_args = input_string[0].split(",")
            input_args = [arg.strip() for arg in input_args]
        else:
            input_args = ("",)

        if input_command in COMMANDS:
            print(COMMANDS[input_command](*input_args))
        else:
            print("No such command")


if __name__ == "__main__":
    main()
