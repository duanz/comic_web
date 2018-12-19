from members import models as MemberModels
from spiders.tools import parser_selector
from spiders.bookSheduler import Scheduler as BookSheduler
from spiders.comicSheduler import Scheduler as ComicSheduler
from django.conf import settings
import logging


def get_queryset():
    return MemberModels.Task.normal.filter(active=True, task_status=MemberModels.TASK_STATUS_DESC.WAIT)


def task():
    logging.info("任务开始执行！")
    queryset = get_queryset()
    logging.info("获取任务列表成功：{}".format(queryset))
    for task in queryset:
        # 处理新增小说任务
        if task.task_type == MemberModels.TASK_TYPE_DESC.BOOK_INSERT:
            task.task_status = MemberModels.TASK_STATUS_DESC.RUNNING
            task.save()
            logging.info("开始小说任务：{}".format(task))
            url = task.content
            s = BookSheduler(
                url=url,
                output_path=settings.UPLOAD_SAVE_PATH,
                parser=parser_selector.get_parser(url),
                fetch_only=None,
                proxy=None,
                verify_ssl=None)
            try:
                s.run()
            except Exception as e:
                logging.error("执行任务失败： {}".format(e))
            task.task_status = MemberModels.TASK_STATUS_DESC.FINISH
            task.save()
            logging.error("执行任务结束")

        # 处理新增漫画任务
        elif task.task_type == MemberModels.TASK_TYPE_DESC.COMIC_INSERT:
            task.task_status = MemberModels.TASK_STATUS_DESC.RUNNING
            task.save()
            logging.info("开始漫画任务：{}".format(task))
            url = task.content
            s = ComicSheduler(
                url=url,
                output_path=settings.UPLOAD_SAVE_PATH,
                parser=parser_selector.get_parser(url),
                fetch_only=None,
                proxy=None,
                verify_ssl=None)
            try:
                s.run()
            except Exception as e:
                logging.error("执行任务失败： {}".format(e))
            task.task_status = MemberModels.TASK_STATUS_DESC.FINISH
            task.save()
            logging.error("执行任务结束")
        else:
            task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
            task.markup = "任务未执行， {}不存在".format(task.task_type)
            task.save()
