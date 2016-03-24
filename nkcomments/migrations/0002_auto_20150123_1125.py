# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0017_auto_20150109_1334'),
        ('nkcomments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentUserOrganisations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.ForeignKey(related_name='user_organizations', to='nkcomments.CustomComment')),
                ('organization', models.ForeignKey(related_name='comments', to='organization.Organization')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='commentuserorganisations',
            unique_together=set([('comment', 'organization')]),
        ),
    ]
