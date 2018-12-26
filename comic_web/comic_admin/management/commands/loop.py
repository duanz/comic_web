from comic_web.utils import time_lib
from comic_web.workers.spiders.work import task
import schedule
import time
from django.core.management.base import BaseCommand
import logging


FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel('INFO'.upper())


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
