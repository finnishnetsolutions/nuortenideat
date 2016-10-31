# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectSlug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField()),
                ('slug', models.SlugField(max_length=64)),
                ('language', models.CharField(default=b'fi', max_length=5, choices=[(b'fi', 'suomi'), (b'sv', 'ruotsi')])),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.AlterUniqueTogether(
            name='objectslug',
            unique_together=set([('content_type', 'slug', 'language')]),
        ),
    ]
