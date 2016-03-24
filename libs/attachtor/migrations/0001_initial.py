# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=255, upload_to=b'')),
                ('original_name', models.CharField(max_length=255)),
                ('size', models.BigIntegerField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UploadGroup',
            fields=[
                ('id', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('object_id', models.IntegerField(null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='uploadgroup',
            unique_together=set([('content_type', 'object_id')]),
        ),
        migrations.AddField(
            model_name='upload',
            name='group',
            field=models.ForeignKey(to='attachtor.UploadGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='upload',
            name='uploader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
