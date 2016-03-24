# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20140915_1827'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('tagging', '0002_auto_20140915_1827'),
    ]

    operations = [
        migrations.CreateModel(
            name='Initiative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='otsikko')),
                ('description', models.TextField(verbose_name='kuvaus')),
                ('visibility', models.SmallIntegerField(default=1, verbose_name='n\xe4kyvyys', choices=[(1, 'Luonnos'), (10, 'Julkinen'), (8, 'Arkistointu')])),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('initiative_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Initiative')),
                ('picture', models.ImageField(upload_to=b'')),
            ],
            options={
                'abstract': False,
            },
            bases=('content.initiative',),
        ),
        migrations.AddField(
            model_name='initiative',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiative',
            name='initiator_organization',
            field=models.ForeignKey(related_name='initiation', to='organization.Organization', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiative',
            name='owners',
            field=models.ManyToManyField(related_name='own_initiatives', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiative',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.initiative_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiative',
            name='tags',
            field=models.ManyToManyField(to='tagging.Tag', verbose_name='aiheet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initiative',
            name='target_organizations',
            field=models.ManyToManyField(to='organization.Organization', verbose_name='kohde organisaatiot'),
            preserve_default=True,
        ),
    ]
