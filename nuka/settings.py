# coding=utf-8

from __future__ import unicode_literals, absolute_import

from datetime import timedelta
from celery.schedules import crontab

"""
    Django settings for nuortenkanava project.
    
    For more information on this file, see
    https://docs.djangoproject.com/en/dev/topics/settings/
    
    For the full list of settings and their values, see
    https://docs.djangoproject.com/en/dev/ref/settings/
    """

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
APP_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.dirname(APP_DIR)
#BASE_DIR = os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'var', 'log', 'django')

DEBUG = False

TEMPLATE_DEBUG = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's2)&75a#tnn2#ayya)cs^wgv@o@cj!*o!hem5*5g#2ehqh@p6^'

ALLOWED_HOSTS = []


# Application definition

PROJECT_APPS = (
                'nuka',
                'account',
                'nkadmin',
                'nkchat',
                'nkcomments',
                'nkvote',
                'nkmoderation',
                'organization',
                'content',
                'tagging',
                'kuaapi',
                'nkmessages',
                'favorite',
                'help',
                'nkwidget',
                'libs.fimunicipality',
                'libs.djcontrib',
                'libs.permitter',
                'libs.attachtor',
                'info',
                'openapi',
                'nkpicturecarousel',
                'omnavi',
                'actions',
                'smslog',
                'campaign',
                )

INSTALLED_APPS = PROJECT_APPS + (
                                 'django.contrib.admin',
                                 'django.contrib.auth',
                                 'django.contrib.contenttypes',
                                 'django.contrib.messages',
                                 'django.contrib.staticfiles',
                                 'django.contrib.humanize',
                                 'django.contrib.sites',
                                 'django.contrib.comments',
                                 'bootstrap3',
                                 'bootstrap3_datetime',
                                 'compressor',
                                 'djangobower',
                                 'redactor',
                                 'django_bleach',
                                 'jstemplate',
                                 'nocaptcha_recaptcha',
                                 'social.apps.django_app.default',
                                 'wkhtmltopdf',
                                 'mptt',
                                 'libs.moderation',
                                 'libs.multilingo',
                                 'rest_framework',
                                 'rest_framework_swagger',
                                 )

COMMENTS_APP = 'nkcomments'

MIDDLEWARE_CLASSES = (
                      'libs.djcontrib.http.middleware.XForwardedForMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.middleware.locale.LocaleMiddleware',
                      'django.middleware.common.CommonMiddleware',
                      'django.middleware.csrf.CsrfViewMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware',
                      'django.middleware.clickjacking.XFrameOptionsMiddleware',
                      'account.middleware.CustomSocialExceptionMiddleware',
                      'libs.djcontrib.http.middleware.NeverCacheMiddleware',
                      'libs.djcontrib.http.middleware.NoSniffMiddleware',
                      )

AUTHENTICATION_BACKENDS = (
                           'django.contrib.auth.backends.ModelBackend',
                           'social.backends.facebook.Facebook2OAuth2',
                           )
TEMPLATE_CONTEXT_PROCESSORS = (
                               'django.contrib.auth.context_processors.auth',
                               'django.core.context_processors.debug',
                               'django.core.context_processors.i18n',
                               'django.core.context_processors.media',
                               'django.core.context_processors.static',
                               'django.core.context_processors.tz',
                               'django.core.context_processors.request',
                               'django.contrib.messages.context_processors.messages',
                               'libs.permitter.context_processors.permitter',
                               'nkchat.context_processors.firebase',
                               'social.apps.django_app.context_processors.backends',
                               'social.apps.django_app.context_processors.login_redirect',
                               'nuka.context_processors.nuka_settings',
                               )

ROOT_URLCONF = 'nuka.urls'

WSGI_APPLICATION = 'nuka.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'fi'

LANGUAGES = (
             ('fi', 'Suomeksi'),
             ('sv', 'På svenska'),
             )

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = False


LOGIN_REDIRECT_URL = '/'

ENV_NAME = os.environ.get('DJANGO_SETTINGS_MODULE', 'dev').split('.')[-1]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
        "KEY_PREFIX": "nuka:%s:cache" % ENV_NAME
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
        "KEY_PREFIX": "nuka:%s:session" % ENV_NAME
}
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AUTH_USER_MODEL = 'account.User'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(APP_DIR, 'static-tmp')

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                       'compressor.finders.CompressorFinder',
                       )

BOWER_INSTALLED_APPS = (
                        'jquery#1.11.1',
                        'underscore#1.8.3',
                        'bootstrap#3.1.1',
                        'bootstrap-multiselect#0.9.8',
                        'bootstrap-sass-official#3.1.1+2',
                        'bootstrap3-datetimepicker#3.1.3',
                        'select2#3.5.1',
                        'select2-bootstrap3-css#1.4.1',
                        'fontawesome#4.2.0',
                        'jquery-form#3.46.0',
                        'masonry#3.1.5',
                        'firebase#1.0.24',
                        'firechat#1.0.0',
                        'mustache#0.8.2',
                        'backfire#0.3.0',
                        'backbone#1.1.0',
                        'backbone-super#1.0.2',
                        'moment#2.8.3',
                        )

BOWER_COMPONENTS_ROOT = STATIC_ROOT


# http://stackoverflow.com/questions/20559698/django-bower-foundation-5-sass-how-to-configure
# http://sass-lang.com/documentation/file.SASS_REFERENCE.html
# http://blog.55minutes.com/2013/01/lightning-fast-sass-reloading-in-rails-32/

SASS_CACHE_PATH = os.path.join(STATIC_ROOT, 'sass')

COMPRESS_PRECOMPILERS = (
                         (
                          'text/x-scss',
                          'sass --scss "{infile}" "{outfile}" '
                          '-I "%s/bower_components" --cache-location="%s"' % (
                                                                              BOWER_COMPONENTS_ROOT,
                                                                              SASS_CACHE_PATH,
                                                                              )
                          ),
                         )

COMPRESS_ENABLED = True


BOOTSTRAP3 = {
    'form_renderers': {
        'default': 'bootstrap3.renderers.FormRenderer',
        'preview': 'libs.bs3extras.renderers.FormPreviewRenderer',
        'notification_options_preview': 'bootstrap3.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'libs.bs3extras.renderers.AccessibleWrapIdFieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
        'preview': 'libs.bs3extras.renderers.WrapIdFieldPreviewRenderer',
        'notification_options_preview': 'account.renderers.'
            'NotificationOptionsFieldPreviewRenderer',
},
}


LOGIN_URL = "/kayttaja/kirjaudu-sisaan/"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'local', 'media')

ENV_NAME = os.environ.get('DJANGO_SETTINGS_MODULE', 'dev').split('.')[-1]

IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = 'imagekit.cachefiles.backends.Simple'
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'
# TODO?: IMAGEKIT_DEFAULT_CACHEFILE_BACKEND ='imagekit.cachefiles.backends.Celery'

REDACTOR_OPTIONS = {}


BLEACH_ALLOWED_TAGS = ['p', 'div', 'a', 'em', 'strong', 'del', 'img',
                       'ul', 'ol', 'li',
                       'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'pre',
                       'table', 'tbody', 'thead', 'tr', 'td', 'th',
                       'iframe']
BLEACH_STRIP_TAGS = True
BLEACH_ALLOWED_ATTRIBUTES = {
    '*': ['style', 'title', ],
    'a': ['href', 'rel', 'target', ],
    'img': ['src', 'alt', ],
    'iframe': ['src', 'frameborder', 'height', 'width', ],
    'td': ['colspan', 'rowspan', ],
}
BLEACH_ALLOWED_STYLES = ['font-family', 'font-weight', 'text-decoration', 'font-variant',
                         'text-align', 'width', 'height', 'margin', 'margin-left',
                         'margin-right', 'margin-top', 'margin-bottom', 'float', ]

SITE_ID = 1

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_PIPELINE = (
                        'social.pipeline.social_auth.social_details',
                        'social.pipeline.social_auth.social_uid',
                        'social.pipeline.social_auth.auth_allowed',
                        'account.pipeline.performed_action',
                        'account.pipeline.social_user',
                        'account.pipeline.prevent_duplicate_signup',
                        'account.pipeline.logged_user',
                        'social.pipeline.social_auth.associate_user',
                        'social.pipeline.social_auth.load_extra_data',
                        'social.pipeline.user.user_details',
                        'account.pipeline.set_messages'
                        )
SOCIAL_AUTH_DISCONNECT_PIPELINE = (
                                   'social.pipeline.disconnect.allowed_to_disconnect',
                                   'social.pipeline.disconnect.get_entries',
                                   'social.pipeline.disconnect.revoke_tokens',
                                   'social.pipeline.disconnect.disconnect',
                                   'account.pipeline.set_disconnect_messages'
                                   )
FIELDS_STORED_IN_SESSION = ["action"]

WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
}

KUA_API = {
    'participants_url': 'https://testi.kuntalaisaloite.fi/api/v1/municipalities',
    'initiative_urls': {
        'fi': 'https://testi.kuntalaisaloite.fi/fi/aloite/%(initiative_id)d',
        'sv': 'https://testi.kuntalaisaloite.fi/sv/initiativ/%(initiative_id)d'
    },
    'ip_restriction': None,
    'enabled': False,
    'simulation': False
}

BROKER_URL = 'redis://localhost:6379/5'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_IGNORE_RESULT = True
CELERY_DEFAULT_QUEUE = 'nuka'
CELERY_ACCEPT_CONTENT = ['json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_SEND_TASK_ERROR_EMAILS = True

CELERYBEAT_SCHEDULE = {
    'synchronize-finnish-municipalties': {
        'task': 'libs.fimunicipality.tasks.sync_municipalities',
        'schedule': timedelta(days=7),
    },
    'synchronize-kua-participants': {
        'task': 'kuaapi.tasks.sync_kua_participants',
        'schedule': timedelta(hours=3),
    },
    """
        'warn-unpublished-ideas': {
        'task': 'content.tasks.warn_unpublished',
        'schedule': crontab(hour=12, minute=10),
        },
        'archive-unpublished-ideas': {
        'task': 'content.tasks.archive_unpublished',
        'schedule': crontab(hour=12, minute=20),
        },
        'remind-untransferred-ideas': {
        'task': 'content.tasks.remind_untransferred',
        'schedule': crontab(hour=12, minute=30),
        },
        'warn-untransferred-ideas': {
        'task': 'content.tasks.warn_untransferred',
        'schedule': crontab(hour=12, minute=40),
        },
        'archive-untransferred-ideas': {
        'task': 'content.tasks.archive_untransferred',
        'schedule': crontab(hour=12, minute=50),
        },
        """
    'chat-users-cleanup': {
        'task': 'nkchat.tasks.cleanup_chat_users',
        'schedule': timedelta(minutes=3),
        'options': {'expires': 60},
    },
    'forceful-chat-users-cleanup': {
        'task': 'nkchat.tasks.cleanup_chat_users',
        'schedule': timedelta(hours=1),
        'options': {'expires': 60},
        'kwargs': {'force': True},
    },
    'daily-notifications': {
        'task': 'actions.tasks.create_daily_notifications',
        'schedule': crontab(hour=0, minute=0),
    },
    'weekly-notifications': {
        'task': 'actions.tasks.create_weekly_notifications',
        'schedule': crontab(day_of_week=6, hour=0, minute=0),
    },
    'sms-log-report': {
        'task': 'smslog.send_sms_log_as_email',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
}
}

TEST_RUNNER = 'nuka.test.runner.TestRunner'
DEFAULT_TEST_PATTERN = 'tests.py'

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

ATTACHMENTS = {
    'max_size': 15 * 1024 * 1024,
    'max_attachments_per_object': 30,
    'max_size_per_uploader': 50 * 1024 * 1024,
    'max_size_per_uploader_timeframe': timedelta(hours=24),
}

LOCALE_PATHS = (
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locale'),
                )

PRACTICE = False  # Is this a practice environment?

FORMAT_MODULE_PATH = 'nuka.formats'


UNPUBLISHED_WARNING_DAYS = 7
UNPUBLISHED_ARCHIVING_DAYS = 30
UNTRANSFERRED_REMIDING_DAYS = 30
UNTRANSFERRED_WARNING_DAYS = 60
UNTRANSFERRED_ARCHIVING_DAYS = 90


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
                                   'openapi.permissions.ReadOnly',
                                   ],
                                   'DEFAULT_PARSER_CLASSES': [
                                                              'rest_framework.parsers.JSONParser',
                                                              'rest_framework.parsers.FormParser',
                                                              ],
                                   'DEFAULT_RENDERER_CLASSES': [
                                                                'rest_framework.renderers.BrowsableAPIRenderer',
                                                                'rest_framework.renderers.JSONRenderer',
                                                                'openapi.renderers.XMLRenderer',
                                                                ]
}

FILE_UPLOAD_ALLOWED_EXTENSIONS = [
                                  'jpg', 'jpeg', 'png', 'gif',
                                  'txt',
                                  'json',
                                  'xml',
                                  'csv',
                                  'mp3', 'ogg',
                                  'mp4', 'avi', 'mpg', 'mpeg', 'mkv',
                                  'pdf',
                                  'doc', 'docx',
                                  'odt', 'ods', 'odp',
                                  'xls', 'xlsx',
                                  'ppt', 'pps', 'pptx', 'ppsx',
                                  ]


OPEN_API = {
    'version': '0.1'
}

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': OPEN_API['version'],
    'doc_expansion': 'list',
    'template_path': 'openapi/docs/index.html',
    'info': {
        'title': 'Open Data API v0.1',
        'description': ''
    # HACK: long html description gets injected by
    # opendata.decorators.swagger_api_description_hack
    },
}

CLAMAV = {
    'enabled': False
}

