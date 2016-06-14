from django.db import migrations

def update_notifications(apps, schema_editor):
    from account.models import NotificationOptions
    from nkcomments.models import CustomComment

    filtered_options = NotificationOptions.objects.filter(
        action_subtype=CustomComment.ACTION_SUB_TYPE_QUESTION_COMMENTED)

    for o in filtered_options.all():
        new_obj = o
        new_obj.pk = None
        new_obj.id = None
        new_obj.action_subtype = CustomComment.ACTION_SUB_TYPE_QUESTION_ANSWERED
        new_obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0025_question_user_email'),
        ('actions', '0009_auto_20150624_1236'),
    ]

    operations = [
        migrations.RunPython(update_notifications),
    ]
