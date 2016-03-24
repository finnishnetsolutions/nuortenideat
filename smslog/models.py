from django.db import models


class SentTxtMessages(models.Model):
    phone_number = models.CharField(max_length=25, null=False,
                                    blank=False, default=None)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_and_save(cls, phone_number):
        sent_message = cls(phone_number=phone_number)
        sent_message.save()
        return sent_message
