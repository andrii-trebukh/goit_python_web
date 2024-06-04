from django.forms import ModelForm, CharField, TextInput, DateField, DateInput, Textarea
from .models import Tag, Author, Quote


class TagForm(ModelForm):

    name = CharField(
        min_length=3,
        max_length=35,
        required=True,
        widget=TextInput()
    )

    class Meta:
        model = Tag
        fields = ['name']


class AuthorForm(ModelForm):

    fullname = CharField(
        min_length=3,
        max_length=50,
        required=True,
        widget=TextInput()
    )
    born_date = DateField(
        required=True,
        input_formats=["%d.%m.%Y"],
        widget=DateInput()
    )
    born_location = CharField(
        min_length=3,
        max_length=150,
        required=True,
        widget=TextInput()
    )
    description = CharField(max_length=4000, required=True, widget=Textarea())

    class Meta:
        model = Author
        fields = ["fullname", "born_date", "born_location", "description"]


class QuoteForm(ModelForm):

    quote = CharField(
        min_length=3,
        max_length=2000,
        required=True,
        widget=TextInput()
    )

    class Meta:
        model = Quote
        fields = ["quote", "author"]
        exclude = ["tags"]
