
from comic_web import celery_app as app
from comic_web.workers.spiders import work


@app.task(ignore_result=True)
def handle_worker_tasks():
    """定时任务：执行Task表中状态为‘WAIT’的任务"""
    work.task()

