from django.db.models.loading import get_apps, get_models
from django.core.management.base import NoArgsCommand
from slug.models import SlugifiedModel


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for app in get_apps():
            for model in get_models(app):
                if issubclass(model, SlugifiedModel):
                    print 'Slugifying %s' % model._meta.verbose_name_plural
                    i = 0
                    for obj in model._default_manager.all().iterator():
                        obj.save()
                        i += 1
                        if not i % 100:
                            print '%d %s slugified' % (i, model._meta.verbose_name_plural)
