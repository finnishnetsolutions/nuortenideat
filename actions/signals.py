import django.dispatch

action_performed = django.dispatch.Signal(providing_args=['created'])