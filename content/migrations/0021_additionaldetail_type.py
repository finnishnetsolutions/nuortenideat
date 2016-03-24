# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0020_decision_given_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionaldetail',
            name='type',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Project-Id-Version: Django\nReport-Msgid-Bugs-To: \nPOT-Creation-Date: 2013-05-02 16:18+0200\nPO-Revision-Date: 2010-05-13 15:35+0200\nLast-Translator: Django team\nLanguage-Team: English <en@li.org>\nLanguage: en\nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n'), (1, 'P\xc4\xc4T\xd6S')]),
            preserve_default=True,
        ),
    ]
