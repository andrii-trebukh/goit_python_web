import json
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import datetime
from .forms import TagForm, AuthorForm, QuoteForm
from .models import Author, Tag, Quote
from .utils import mongodb_get, scrape


# Create your views here.
def top_ten():
    return Tag.objects.all().annotate(count=Count("quote")) \
        .values("name", "count").exclude(count=0) \
        .order_by("-count")[:10]


def main(request, page=1):
    quotes = Quote.objects.all()
    prev_page = page - 1 if page != 1 else None
    next_page = page + 1
    first_qoute = (page - 1) * 10
    last_quote = first_qoute + 9
    if last_quote >= len(quotes) - 1:
        last_quote = len(quotes) - 1
        next_page = None

    if first_qoute > len(quotes) - 1:
        prev_page = next_page = None
        output = []
    else:
        output = quotes[first_qoute:last_quote + 1]

    return render(
        request,
        'quotesapp/index.html',
        {
            "quotes": output,
            "prev_page": prev_page,
            "next_page": next_page,
            "top_ten": top_ten(),
        }
    )


def tag(request, tag_name):
    quotes = Quote.objects.filter(
        tags__in=Tag.objects.filter(name=tag_name)
    )
    return render(
        request,
        'quotesapp/index.html',
        {
            "quotes": quotes,
            "prev_page": False,
            "next_page": False,
            "top_ten": top_ten(),
        }
    )


@login_required
def add_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotesapp:main')
        return render(request, 'quotesapp/add-tag.html', {'form': form})

    return render(request, 'quotesapp/add-tag.html', {'form': TagForm()})


@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotesapp:main')
        return render(request, "quotesapp/add-author.html", {'form': form})

    return render(request, "quotesapp/add-author.html", {'form': AuthorForm()})


@login_required
def quote(request):
    authors = Author.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote = form.save()
            choice_tags = Tag.objects.filter(
                name__in=request.POST.getlist('tags')
            )
            for choice_tag in choice_tags.iterator():
                new_quote.tags.add(choice_tag)

            return redirect(to='quotesapp:main')
        return render(
            request,
            "quotesapp/quote.html",
            {'authors': authors, 'tags': tags, 'form': form}
        )

    return render(
        request,
        "quotesapp/quote.html",
        {'authors': authors, 'tags': tags, 'form': QuoteForm()}
    )


def author(request, author_id):
    show_author = get_object_or_404(Author, pk=author_id)
    return render(request, 'quotesapp/author.html', {"author": show_author})


@login_required
def seed(request, source=None):
    if source == "mongodb":

        for in_author in mongodb_get.authors():

            if Author.objects.filter(fullname=in_author["fullname"]):
                continue

            Author(
                fullname=in_author["fullname"],
                born_date=in_author["born_date"],
                born_location=in_author["born_location"],
                description=in_author["description"]
            ).save()

        for quote in mongodb_get.quotes():

            if Quote.objects.filter(quote=quote["quote"]):
                continue

            author = Author.objects.filter(fullname=quote["author"])
            if not author:
                continue

            add_quote = Quote(
                author=author[0],
                quote=quote["quote"]
            )
            add_quote.save()

            for tag in quote["tags"]:
                add_tag = Tag.objects.filter(name=tag)
                if add_tag:
                    add_tag = add_tag[0]
                else:
                    add_tag = Tag(
                        name=tag
                    )
                    add_tag.save()
                add_quote.tags.add(add_tag)

    elif source == "scrapy":
        scrape.run_spiders()

        path = Path(__file__).parent.joinpath("utils/authors.json")
        with open(path, "r", encoding="utf-8") as fd:
            authors = json.load(fd)

        for author in authors:

            if Author.objects.filter(fullname=author["fullname"]):
                continue

            Author(
                fullname=author["fullname"],
                born_date=datetime.strptime(author["born_date"], r"%B %d, %Y"),
                born_location=author["born_location"],
                description=author["description"]
            ).save()

        path = Path(__file__).parent.joinpath("utils/qoutes.json")
        with open(path, "r", encoding="utf-8") as fd:
            quotes = json.load(fd)

        for quote in quotes:

            if Quote.objects.filter(quote=quote["quote"]):
                continue

            author = Author.objects.filter(fullname=quote["author"])
            if not author:
                continue

            add_quote = Quote(
                author=author[0],
                quote=quote["quote"]
            )
            add_quote.save()

            for tag in quote["tags"]:
                add_tag = Tag.objects.filter(name=tag)
                if add_tag:
                    add_tag = add_tag[0]
                else:
                    add_tag = Tag(
                        name=tag
                    )
                    add_tag.save()
                add_quote.tags.add(add_tag)

    else:
        return render(request, 'quotesapp/seed.html', {"seed_done": False})

    return render(request, 'quotesapp/seed.html', {"seed_done": True})
