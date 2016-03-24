# coding=utf-8

from __future__ import unicode_literals

from httplib import BAD_REQUEST
import os

from django.conf import settings
from django.core.files.base import ContentFile, File
from django.test.utils import override_settings

from libs.attachtor.utils import get_upload_group_id
from nuka.test.testcases import TestCase
from ..utils import get_upload_token
from ..models import UploadGroup, Upload

TEST_URLS = '.'.join(__package__.split('.') + ['urls'])


@override_settings(ROOT_URLCONF=TEST_URLS)
class AttachmentUploadTest(TestCase):
    def setUp(self):
        self.test_file = os.path.join(
            os.path.dirname(__file__),
            'testdata/cat.png'
        )

    def test_upload_attachment(self):
        self.assertEqual(UploadGroup.objects.count(), 0)
        self.assertEqual(Upload.objects.count(), 0)
        upload_group_id = get_upload_group_id(None)
        resp = self.client.post('/upload/%(upload_group_id)s%(upload_token)s/' % {
            'upload_group_id': upload_group_id,
            'upload_token': get_upload_token(upload_group_id)
        }, {
            'file': open(self.test_file, 'rb')
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 1)
        upload = Upload.objects.first()
        group = upload.group
        self.assertEqual(group.pk, upload_group_id)

    def test_upload_with_bad_token(self):
        upload_group_id = get_upload_group_id(None)
        upload_token = get_upload_token(upload_group_id)
        upload_token = upload_token[:-5] + 'aaaaa'
        resp = self.client.post('/upload/%(upload_group_id)s%(upload_token)s/' % {
            'upload_group_id': upload_group_id,
            'upload_token': upload_token
        }, {
            'file': open(self.test_file, 'rb')
        })
        self.assertEqual(resp.status_code, BAD_REQUEST)
        self.assertEqual(UploadGroup.objects.count(), 0)

    def tearDown(self):
        for u in Upload.objects.all():
            u.file.delete()


if __package__ in settings.INSTALLED_APPS:
    from .models import Blog

    @override_settings(ROOT_URLCONF=TEST_URLS, CELERY_ALWAYS_EAGER=True)
    class RedactorFieldSaveTest(TestCase):
        def setUp(self):
            self.upload_group_id = get_upload_group_id(None)
            self.upload_signature = ''.join([self.upload_group_id,
                                             get_upload_token(self.upload_group_id)])
            upload_group = UploadGroup.objects.create(
                pk=self.upload_group_id
            )
            test_file = ContentFile('wasaap', 'test.txt')
            self.upload = Upload.objects.create(
                group=upload_group,
                original_name='test.txt',
                file=test_file,
                size=test_file.size
            )

        def test_create_and_update_blog_with_attachments(self):
            self.assertEqual(Blog.objects.count(), 0)
            self.assertEqual(UploadGroup.objects.count(), 1)
            self.assertEqual(Upload.objects.count(), 1)

            resp = self.client.post('/blogs/create/', {
                'title': 'Hallo',
                'content': '<img src="%s">' % self.upload.file.url,
                'upload_ticket': self.upload_signature
            })
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.content, 'success')
            self.assertEqual(Blog.objects.count(), 1)

            # There should still be one upload in one upload group
            self.assertEqual(UploadGroup.objects.count(), 1)
            self.assertEqual(Upload.objects.count(), 1)

            upload_group = UploadGroup.objects.first()
            upload = Upload.objects.first()

            # the only Upload should belong to the only UploadGroup
            self.assertEqual(upload.group_id, upload_group.pk)

            # content_type and object_id for the UploadGroup should now be set
            self.assertIsNotNone(upload_group.content_type)
            self.assertIsNotNone(upload_group.object_id)

            # upload_group primary key should have changed
            self.assertNotEqual(upload_group.pk, self.upload_group_id)
            self.assertTrue(os.path.exists(self.upload.file.path))

            test_file2 = ContentFile('wasaap2', 'test2.txt')
            new_upload = Upload.objects.create(
                group=upload_group,
                original_name='test2.txt',
                file=test_file2,
                size=test_file2.size
            )
            self.assertTrue(os.path.exists(new_upload.file.path))
            resp = self.client.post('/blogs/%d/edit/' % upload_group.object_id, {
                'title': 'Hallo',
                'content': '<a href="%s">jellow</a>' % new_upload.file.url,
                'upload_ticket': self.upload_signature
            })
            self.assertEqual(Upload.objects.count(), 1)
            self.assertTrue(os.path.exists(new_upload.file.path))
            self.assertFalse(os.path.exists(self.upload.file.path))

        def test_delete_attachments_when_blog_deleted(self):
            blog = Blog(
                title='hello',
                content='<img src="%s">' % self.upload.file.url
            )
            setattr(blog, '_attachtor_upload_group_id', self.upload_group_id)
            blog.save()
            self.assertEqual(UploadGroup.objects.count(), 1)
            self.assertEqual(Upload.objects.count(), 1)
            self.assertTrue(os.path.exists(self.upload.file.path))
            blog.delete()
            self.assertFalse(os.path.exists(self.upload.file.path))
            self.assertEqual(UploadGroup.objects.count(), 0)
            self.assertEqual(Upload.objects.count(), 0)

        def tearDown(self):
            for u in Upload.objects.all():
                u.file.delete()
