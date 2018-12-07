# import logging
# from django.core.management.base import BaseCommand
# from mall_web.workers.backup import daily_backup, backup

# FORMAT = '%(asctime)s - %(message)s'
# logging.basicConfig(format=FORMAT)
# logging.getLogger().setLevel('INFO'.upper())


# class Command(BaseCommand):
#     """
#     数据备份，可选 -t （任务id）参数
#     """
#     help = 'Backup.'

#     def add_arguments(self, parser):
#         parser.add_argument('-t', dest='task_id', help='id of backup task record')

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS('Backup start ...'))

#         task_id = options.get('task_id')
#         if task_id:
#             backup(task_id)
#         else:
#             daily_backup()

#         self.stdout.write(self.style.SUCCESS('Finish backup data.'))
