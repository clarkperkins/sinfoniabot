from django.db import models


class Count(models.Model):
    MAX_COUNT = 10

    count = models.IntegerField('Count')
