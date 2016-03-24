from django.test import TestCase

from .models import SentTxtMessages


class SmsLogTest(TestCase):
    def test_create_and_save(self):
        sent_message = SentTxtMessages.create_and_save('+358456789123')
        self.assertGreater(sent_message.created.month, 0, 'Created time error')
