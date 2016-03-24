# coding=utf-8

from __future__ import unicode_literals

from django.db import models

from ..models.fields import RedactorAttachtorField


class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = RedactorAttachtorField()
