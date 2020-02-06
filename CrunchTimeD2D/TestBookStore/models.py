from django.db import models
from django.urls import reverse


class OnixFile(models.Model):
    data = models.TextField()