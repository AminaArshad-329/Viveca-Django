from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmiradio.settings')

# app = Celery('mmiradio',backend='amqp', broker='amqp://mmi:mmiradio@localhost/mmiradio')
app = Celery('mmiradio', backend='amqp', broker='amqp://mmi:mmiradio@10.208.161.122/mmiradio')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_RESULT_BACKEND='celery.backends.database:DatabaseBackend',
)
