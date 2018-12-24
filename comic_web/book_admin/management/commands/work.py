from comic_web.utils import time_lib
import schedule
import time
from members import models as MemberModels
from comic_web.workers.spiders.tools import parser_selector
from comic_web.workers.spiders.bookSheduler import Scheduler as BookSheduler
from comic_web.workers.spiders.comicSheduler import Scheduler as ComicSheduler
from django.conf import settings
from django.core.management.base import BaseCommand
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
                task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
                task.save()

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
                task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
                task.save()

            task.task_status = MemberModels.TASK_STATUS_DESC.FINISH
            task.save()
            logging.error("执行任务结束")
        else:
            task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
            task.markup = "任务未执行， {}不存在".format(task.task_type)
            task.save()


SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7


def fill_content(content, fill='*', str_len=50):
    return '{0:{fill}^{str_len}}'.format(content, fill=fill, str_len=str_len)


def log_task_run(content, fill='*', str_len=50, is_end=False):
    _content = '{} {}'.format(content, 'END' if is_end else 'START')
    logging.info(fill * str_len)
    logging.info(fill_content(_content, fill=fill, str_len=str_len))
    logging.info(fill * str_len)


class Command(BaseCommand):
    """
    后台循环任务：
        - 关闭超时订单
        - 完成超时收货
        - 每日备份
    """
    help = 'Load initial data for new project.'

    def handle(self, *args, **options):
        """RUN TASK LOOP"""

        # 每日任务(凌晨执行)
        def _day_work():
            log_task_run('DAILY_TASK')
            task()
            log_task_run('DAILY_TASK', is_end=True)

        # 每小时任务
        def _hour_work():
            pass

        # 每分钟任务(不放置耗时任务)
        def _minute_work():
            log_task_run('DAILY_TASK')
            task()
            log_task_run('DAILY_TASK', is_end=True)

        # 设置每日任务的执行小时(范围 0~23) 3表示凌晨3点,
        run_hour_in_24 = 3
        run_hour = time_lib.get_sys_hour_by_cst_hour(run_hour_in_24)
        run_hour_str = '{:0>2d}:00'.format(run_hour)

        schedule.every().day.at(run_hour_str).do(_day_work)
        schedule.every().hour.do(_hour_work)
        schedule.every().minutes.do(_minute_work)

        self.stdout.write(self.style.SUCCESS('Loop tasks start ...'))
        while True:
            schedule.run_pending()
            time.sleep(20 * SECOND)
