from django.db import models


# Create your models here.
class Author(models.Model):
    fullname = models.CharField(max_length=50, null=False, unique=True)
    born_date = models.DateTimeField(null=False)
    born_location = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=4000, null=False)

    def __str__(self):
        return f"{self.fullname}"

    @property
    def born_date_formatted(self):
        return self.born_date.strftime(r"%B %d, %Y")


class Tag(models.Model):
    name = models.CharField(max_length=35, null=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class Quote(models.Model):
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    quote = models.CharField(max_length=2000, null=False, unique=True)

    def __str__(self):
        return f"{self.tags}"

    @property
    def tags_all(self):
        return self.tags.all()
