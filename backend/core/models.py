from django.db import models

# Since we are using MongoDB, we won't use Django's ORM, but you can define models for structure
class Collection(models.Model):
    name = models.CharField(max_length=200)
