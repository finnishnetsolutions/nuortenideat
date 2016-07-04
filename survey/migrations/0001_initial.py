# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import survey.models
import libs.multilingo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0027_auto_20160527_1131'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('show_results', models.SmallIntegerField(null=True, verbose_name='Vastausten n\xe4ytt\xe4minen')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=10000, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyElement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('text', libs.multilingo.models.fields.MultilingualTextField(default=None, max_length=255, blank=True, help_text=None, null=True, verbose_name='vaihtoehto')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyPage',
            fields=[
                ('surveyelement_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='survey.SurveyElement')),
            ],
            options={
                'abstract': False,
            },
            bases=('survey.surveyelement',),
        ),
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('surveyelement_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='survey.SurveyElement')),
                ('text', libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='kysymys')),
                ('instruction_text', libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, max_length=800, verbose_name='ohjeteksti', blank=True)),
                ('required', models.BooleanField(default=False, verbose_name='pakollinen')),
                ('type', models.IntegerField(choices=[(1, 'Yksivalinta'), (2, 'Monivalinta'), (3, 'Tekstikentt\xe4'), (4, 'Numerokentt\xe4')])),
            ],
            options={
                'abstract': False,
            },
            bases=('survey.surveyelement',),
        ),
        migrations.CreateModel(
            name='SurveySubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('client_identifier', models.ForeignKey(to='account.ClientIdentifier', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveySubmitter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitter_id', models.CharField(default=survey.models.create_submitter_id, unique=True, max_length=32)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(related_name='survey_submitter', null=True, default=None, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveySubtitle',
            fields=[
                ('surveyelement_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='survey.SurveyElement')),
                ('text', libs.multilingo.models.fields.MultilingualTextField(default='', help_text=None, max_length=255, verbose_name='v\xe4liotsikko')),
            ],
            options={
                'abstract': False,
            },
            bases=('survey.surveyelement',),
        ),
        migrations.AddField(
            model_name='surveysubmission',
            name='submitter',
            field=models.ForeignKey(to='survey.SurveySubmitter', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveysubmission',
            name='survey',
            field=models.ForeignKey(related_name='submissions', to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='surveysubmission',
            unique_together=set([('survey', 'submitter')]),
        ),
        migrations.AddField(
            model_name='surveyoption',
            name='question',
            field=models.ForeignKey(related_name='options', to='survey.SurveyQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyelement',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_survey.surveyelement_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyelement',
            name='survey',
            field=models.ForeignKey(related_name='elements', to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyanswer',
            name='option',
            field=models.ForeignKey(related_name='answers', to='survey.SurveyOption', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyanswer',
            name='question',
            field=models.ForeignKey(related_name='answers', to='survey.SurveyQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyanswer',
            name='submission',
            field=models.ForeignKey(related_name='answers', to='survey.SurveySubmission'),
            preserve_default=True,
        ),
    ]
