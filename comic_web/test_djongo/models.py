from djongo import models

class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()


class MetaData(models.Model):
    n_pingbacks = models.IntegerField()
    rating = models.IntegerField()


class Author(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

        
    def __str__(self):
        return self.name

class Entry(models.Model):
    blog = models.EmbeddedModelField(
        model_container=Blog,
    )
    meta_data = models.EmbeddedModelField(
        model_container=MetaData,
    )

    headline = models.CharField(max_length=255)
    body_text = models.TextField()

    authors = models.ArrayModelField(
        model_container=Author,
    )
    n_comments = models.IntegerField()

    def __str__(self):
        return self.headline