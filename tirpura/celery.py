# project_root/project_name/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tirpura.settings')

app = Celery('tirpura')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
