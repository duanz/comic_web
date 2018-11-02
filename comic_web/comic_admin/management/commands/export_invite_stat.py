# import logging
# from django.core.management.base import BaseCommand
# from mall_web.workers.export_invite_stat import export_invite_stat_excel

# FORMAT = '%(asctime)s - %(message)s'
# logging.basicConfig(format=FORMAT)
# logging.getLogger().setLevel('INFO'.upper())


# class Command(BaseCommand):
#     """
#     导出邀请返利数据Excel文件，必须指定 -t （任务id）参数
#     """
#     help = 'Export invite stat excel.'

#     def add_arguments(self, parser):
#         parser.add_argument('-t', dest='task_id', help='id of export task record')

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS('Export start ...'))

#         task_id = options.get('task_id')
#         if not task_id:
#             self.stdout.write(self.style.ERROR('Miss task_id.'))
#         else:
#             export_invite_stat_excel(task_id)
#         self.stdout.write(self.style.SUCCESS('Finish export.'))
