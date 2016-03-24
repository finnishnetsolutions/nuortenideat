# coding=utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.db import models
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.dispatch.dispatcher import receiver
from actions.signals import action_performed
from nuka.utils import send_email, render_email_template


class ActionTypeMixin(object):

    def __init__(self):
        self._pk_field = 'content_type_id'
        self._type_field = 'type'
        self._subtype_field = 'subtype'

    @property
    def unique_type(self):
        pk_prop = getattr(self, self._pk_field)
        type_prop = getattr(self, self._type_field)
        subtype_prop = getattr(self, self._subtype_field)
        return "{0}.{1}.{2}".format(pk_prop, type_prop, subtype_prop)

    @property
    def types_combined(self):
        type_prop = getattr(self, self._type_field)
        subtype_prop = getattr(self, self._subtype_field)
        return "{0}.{1}".format(type_prop, subtype_prop)


class Action(models.Model, ActionTypeMixin):
    TYPE_CREATED = 'created'
    TYPE_UPDATED = 'updated'
    TYPE_DELETED = 'deleted'
    TYPE_CHOICES = ((TYPE_CREATED, TYPE_CREATED),
                    (TYPE_UPDATED, TYPE_UPDATED),
                    (TYPE_DELETED, TYPE_DELETED),)

    ROLE_CONTENT_OWNER = 'content-owner'
    ROLE_ORGANIZATION_CONTACT = 'organization-contact'
    ROLE_MODERATOR = 'moderator'

    USER_TYPE_NORMAL = 0
    USER_TYPE_MODERATOR = 1
    USER_TYPE_CONTACT_PERSON = 2

    GROUP_ALL = [USER_TYPE_NORMAL, USER_TYPE_CONTACT_PERSON, USER_TYPE_MODERATOR]
    GROUP_MODERATORS = [USER_TYPE_MODERATOR, ]
    GROUP_CONTACTS = [USER_TYPE_CONTACT_PERSON]

    actor = models.ForeignKey('account.User', null=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=16)
    subtype = models.CharField(max_length=100, default='')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    created = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        self.notification_recipients = []

    def add_notification_recipients(self, role, recipients):
        self.notification_recipients.append((role, recipients))

    def create_notifications(self):
        if hasattr(self.content_object, 'fill_notification_recipients'):
            self.content_object.fill_notification_recipients(self)
        objects = []
        for role, recipient in self.notification_recipients:
            subscription_option_obj = self.user_is_subscribed(recipient, role)
            if subscription_option_obj:
                obj = Notification(recipient=recipient, action=self, role=role)
                if subscription_option_obj.notify_at_once:
                    obj.send_instantly = True
                obj.save()
                objects.append(obj)

        self.notify_subscribed_users(objects)

    def notify_subscribed_users(self, notifications):
        for v in notifications:
            if v.send_instantly:
                self.notify_subscribed_user(v.recipient, v.role, v)

    def notify_subscribed_user(self, user, role, notification=None):
        if not self.user_is_subscribed(user, role):
            return False
        template_pattern = 'notifications/email/{0}/{1}.{2}.{3}.txt'
        template = template_pattern.format(self.content_type.app_label,
                                           self.content_type.model,
                                           self.types_combined,
                                           role, )

        msg_context = {'object': self, 'user': user}
        subject, body = render_email_template(template, msg_context)
        send_mail(subject=subject, message=body,
                  recipient_list=[user.settings.email, ], from_email=None)

        sent_email_obj = SentEmails(notification=notification, email=user.settings.email)
        sent_email_obj.save()

    def user_is_subscribed(self, user, role):
        for n in user.user_notifications.all():
            if not n.cancelled and n.unique_type == self.unique_type \
                    and n.role == role:
                return n
        return False

    def user_has_daily_subscription(self, user, role):
        option = self.user_is_subscribed(user, role)
        return True if option and option.notify_daily else False

    def user_has_weekly_subscription(self, user, role):
        option = self.user_is_subscribed(user, role)
        return True if option and option.notify_weekly else False


class NotificationQuerySet(models.QuerySet):

    def get_by_date(self, dt):
        return self.filter(action__created__gte=dt)

    def get_recipients(self):
        return set([notification.recipient for notification in self.select_related('recipient')])

    def format_for_user(self, user, subscription_check_method):
        key_pattern = '{}_{}_{}_{}'
        notifications = {}
        for v in self.filter(recipient=user):
            if hasattr(v.action, subscription_check_method):
                if getattr(v.action, subscription_check_method)(v.recipient, v.role):
                    key = key_pattern.format(v.action.content_object.__class__.__name__,
                                             v.role.replace('-', '_'),
                                             v.action.type.replace('-', '_'),
                                             v.action.subtype.replace('-', '_'))
                    if key not in notifications:
                        notifications[key] = []
                    notifications[key].append(v)
        return notifications


class Notification(models.Model):
    action = models.ForeignKey(Action, related_name='notifications')
    recipient = models.ForeignKey('account.User', blank=True, null=True,
                                  related_name='notifications')
    role = models.CharField(max_length=50)
    send_instantly = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    objects = NotificationQuerySet.as_manager()

    def __unicode__(self):
        return '%s#%d' % (self.__class__.__name__, self.pk)

    class Meta:
        unique_together = (('action', 'recipient', 'role'), )
        get_latest_by = 'action__created'
        ordering = ('-id', )


class SentEmails(models.Model):
    notification = models.ForeignKey(Notification, related_name='sent_emails', null=True)
    email = models.CharField(max_length=254)
    created = models.DateTimeField(auto_now_add=True)


### ACTION PROCESSING ###
def _generate_notifications_post_save(instance, created, **kwargs):
    if not created:
        return
    from tasks import create_notifications
    create_notifications(instance)


signals.post_save.connect(_generate_notifications_post_save, sender=Action)


@receiver(action_performed)
def create_action_objects(sender=None, created=False, **kwargs):
    action_type = Action.TYPE_CREATED if created else Action.TYPE_UPDATED
    if action_type == Action.TYPE_CREATED and not sender.create_created_action():
        return
    if action_type == Action.TYPE_UPDATED and not sender.create_updated_action():
        return
    content_type = ContentType.objects.get_for_model(sender, for_concrete_model=False)
    action_kwargs = sender.get_action_kwargs(action_type)

    if 'subtype' in action_kwargs and len(action_kwargs['subtype']):
        for subtype in action_kwargs['subtype']:
            new_kwargs = action_kwargs
            new_kwargs['subtype'] = subtype
            create_action_object(action_type, content_type, sender.pk, **new_kwargs)
    else:
        create_action_object(action_type, content_type, sender.pk, **action_kwargs)


def create_action_object(action_type, content_type, object_id, **action_kwargs):
    Action.objects.create(type=action_type, content_type=content_type,
                          object_id=object_id, **action_kwargs)


def _send_action_performed(instance, created, **kwargs):
    action_performed.send(sender=instance, created=created)


class ActionRelation(GenericRelation):
    def __init__(self):
        super(ActionRelation, self).__init__(
            Action, content_type_field='content_type', object_id_field='object_id')

    def contribute_to_class(self, cls, name):
        super(ActionRelation, self).contribute_to_class(cls, name)
        if not cls._meta.abstract and cls.connect_post_save:
            signals.post_save.connect(_send_action_performed, sender=cls)


class ActionGeneratingModelMixin(models.Model):
    actions_by_target = ActionRelation()
    connect_post_save = True

    def fill_notification_recipients(self, action):
        raise NotImplementedError

    def get_action_kwargs(self, type):
        if type == Action.TYPE_CREATED:
            return self.action_kwargs_on_create()
        if type == Action.TYPE_UPDATED:
            return self.action_kwargs_on_update()

    def action_kwargs_on_update(self):
        raise NotImplementedError

    def action_kwargs_on_create(self):
        raise NotImplementedError

    def create_created_action(self):
        return True

    def create_updated_action(self):
        return False

    class Meta:
        abstract = True
