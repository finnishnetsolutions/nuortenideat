# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.-]+$', 'Enter a valid username.', 'invalid')])),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('status', models.SmallIntegerField(max_length=10, verbose_name='tila', choices=[(0, 'Odottaa aktivointia'), (1, 'Aktiivinen'), (5, 'Arkistoitu'), (10, 'S\xe4hk\xf6posti vahvistamatta')])),
                ('joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='liittynyt', auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='muokattu')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'K\xe4ytt\xe4j\xe4',
                'verbose_name_plural': 'K\xe4ytt\xe4j\xe4t',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('language', models.CharField(default='fi', max_length=5, choices=[('fi', 'suomi'), ('sv', 'ruotsi')])),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='s\xe4hk\xf6posti')),
                ('phone_number', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('user', models.OneToOneField(related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'K\xe4ytt\xe4j\xe4asetus',
                'verbose_name_plural': 'K\xe4ytt\xe4j\xe4asetukset',
            },
            bases=(models.Model,),
        ),
    ]
