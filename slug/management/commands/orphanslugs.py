from django.core.management.base import NoArgsCommand
from slug.models import ObjectSlug


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        i, deleted = 0, 0
        for slug in ObjectSlug.objects.all():
            if slug.object is None:
                print 'deleting %s' % slug
                slug.delete()
                deleted +=1
            i += 1
            if not i % 100:
                print 'gone thru %d slugs, %d orphans deleted' % (i, deleted)
        print 'DONE! went thru %d slugs, %d orphans deleted' % (i, deleted)
