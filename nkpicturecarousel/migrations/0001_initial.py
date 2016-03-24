# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nkpicturecarousel.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PictureCarouselImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default='fi', help_text='Lis\xe4\xe4 kuvat vain kerran per kieli.', max_length=5, verbose_name='kieli', choices=[('fi', 'suomi'), ('sv', 'ruotsi')])),
                ('image_large', nkpicturecarousel.models.CarouselImageField(upload_to_size='1140-2560x330', height=330, width=2560, help_text='2560x330 px (1140 px)', verbose_name='iso')),
                ('image_medium', nkpicturecarousel.models.CarouselImageField(upload_to_size='940-2560x330', height=330, width=2560, help_text='2560x330 px (940 px)', verbose_name='keskikoko')),
                ('image_small', nkpicturecarousel.models.CarouselImageField(upload_to_size='940x330', height=330, width=940, help_text='940x330 px', verbose_name='pieni')),
                ('alt_text', models.CharField(max_length=255, verbose_name='alt-teksti')),
            ],
            options={
                'verbose_name': 'kuvan kieliversio',
                'verbose_name_plural': 'kuvan kieliversiot',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PictureCarouselSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Nimi')),
                ('is_active', models.BooleanField(default=True, verbose_name='aktiivinen')),
            ],
            options={
                'verbose_name': 'kuvakarusellin kuva',
                'verbose_name_plural': 'kuvakarusellin kuvat',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='picturecarouselimage',
            name='carousel_set',
            field=models.ForeignKey(related_name='images', to='nkpicturecarousel.PictureCarouselSet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='picturecarouselimage',
            unique_together=set([('carousel_set', 'language')]),
        ),
    ]
