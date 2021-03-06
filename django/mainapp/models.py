from django.db import models


class BaseModel(models.Model):
    """
    prevent PyCharm from complaining on .objects-attribute
    source: https://stackoverflow.com/a/56845199/333403
    """

    objects = models.Manager()

    class Meta:
        abstract = True

    def __repr__(self):
        name = getattr(self, "name", "<noname>")
        return f'<{type(self).__name__} "{name}">'

    def repr(self):
        return repr(self)


class SourceDocument(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, null=True, blank=False)
    source_uri = models.CharField(max_length=1000, null=True, blank=False)


class Tag(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, null=True, blank=False)

    # this is to handle localized tag names:
    label = models.CharField(max_length=1000, null=True, blank=False)


class Directive(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, null=True, blank=False)
    text = models.CharField(max_length=10000, null=True, blank=True)
    source_document = models.ForeignKey(SourceDocument, on_delete=models.CASCADE, null=False)
    tags = models.ManyToManyField(Tag)
    section = models.CharField(
        max_length=100,
        null=True,
        blank=False,
    )


class GeographicEntity(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, null=True, blank=False)
    applying_directives = models.ManyToManyField(Directive)
