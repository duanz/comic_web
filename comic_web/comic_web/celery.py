from __future__ import absolute_import, unicode_literals
import os
import datetime

from celery import Celery
from celery import task
from django.conf import settings
from celery.schedules import crontab
#获取当前文件夹名，即为该Django的项目名

project_name = os.path.split(os.path.abspath('.'))[-1]

project_settings = '%s.settings' % project_name

#设置环境变量

os.environ.setdefault('DJANGO_SETTINGS_MODULE', project_settings)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', "comic_web.settings")

#实例化Celery

app = Celery(project_name)
# app = Celery("comic_web")

#使用django的settings文件配置celery

app.config_from_object(settings, namespace="CELERY")
# app.config_from_object("django.conf:settings", namespace="CELERY")

#Celery加载所有注册的应用

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# app.conf.update(
#     CELERYBEAT_SCHEDULE = {
#         'handle_proxy_ips_task': {
#             'task': 'comic_web.comic_admin.tasks.get_proxy_ip_list',
#             'schedule':  datetime.timedelta(seconds=10),
#             'args': ()
#         }
#     }
# )