from members import models as MemberModels
from comic_web.workers.spiders.tools import parser_selector
from comic_web.workers.spiders.bookSheduler import Scheduler as BookSheduler
from comic_web.workers.spiders.comicSheduler import Scheduler as ComicSheduler
from django.conf import settings
import logging


FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel('INFO'.upper())


def get_queryset():
    return MemberModels.Task.normal.filter(active=True, task_status=MemberModels.TASK_STATUS_DESC.WAIT)


def task():
    logging.info("任务开始执行！")
    queryset = get_queryset()
    logging.info("获取任务列表成功：{}".format(queryset))
    for task in queryset:
        # 处理新增小说任务
        if task.task_type in [MemberModels.TASK_TYPE_DESC.BOOK_INSERT, MemberModels.TASK_TYPE_DESC.COMIC_INSERT]:

            task.task_status = MemberModels.TASK_STATUS_DESC.RUNNING
            task.save()
            logging.info("开始任务：{}".format(task))

            url = task.content
            if task.task_type == MemberModels.TASK_TYPE_DESC.BOOK_INSERT:
                s = BookSheduler(
                    url=url,
                    output_path=settings.UPLOAD_SAVE_PATH,
                    parser=parser_selector.get_parser(url)
                )
            elif task.task_type == MemberModels.TASK_TYPE_DESC.COMIC_INSERT:
                s = ComicSheduler(
                    url=url,
                    output_path=settings.UPLOAD_SAVE_PATH,
                    parser=parser_selector.get_parser(url)
                )

            try:
                s.run()
            except Exception as e:
                logging.error("执行任务失败： {}".format(e))
                task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
                task.save()

            task.task_status = MemberModels.TASK_STATUS_DESC.FINISH
            task.save()
            logging.error("执行任务结束")

        else:
            task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
            task.markup = "任务未执行， {}不存在".format(task.task_type)
            task.save()
