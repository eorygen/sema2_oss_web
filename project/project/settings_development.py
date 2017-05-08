from django.conf import settings

import os

LOG_FILEPATH = os.path.join(settings.BASE_DIR, '..', 'logs', 'app.log')
TASK_LOG_FILEPATH = os.path.join(settings.BASE_DIR, '..', 'logs', 'task.log')

CERTS_DIR = os.path.join(settings.BASE_DIR, '..', 'certs')
IOS_PUSH_CERT_NAME = 'sema_dev_push_cert.pem'

MEDIA_ROOT = os.path.join(settings.BASE_DIR, '..', 'media')
