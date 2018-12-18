import logging
from django.core.management.base import BaseCommand
# from workers.comic_spiders import main
from workers.book_spiders.schedulerToDB import Scheduler


FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel('INFO'.upper())


class Command(BaseCommand):
    """
    导出邀请返利数据Excel文件，必须指定 -t （任务id）参数
    """
    help = 'Export invite stat excel.'

    def add_arguments(self, parser):
        print("======11111=====", parser)
        parser.add_argument('-u', dest='url', help='url for get comic')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Export start ...'))

        url = options.get('url')
        print(args)
        print("----------")
        print(options)
        if not url:
            self.stdout.write(self.style.ERROR('Miss url.'))
        else:
            self.start_ttt(url)
            # self._save_chapter_db(1, "2")
        self.stdout.write(self.style.SUCCESS('Finish export.'))

    def start_ttt(self, url):
        from workers.comic_spiders import parser_selector

        s = Scheduler(
            url=url,
            output_path='./output',
            parser=parser_selector.get_parser(url),
            fetch_only=None,
            proxy=None,
            verify_ssl=None)
        # s = Scheduler(url=args.url, output_path=args.output_path, parser=parser_selector.get_parser(args.url), fetch_only=args.fetch_only, proxy=args.proxy, verify_ssl=args.verify_ssl)
        print(1111111111111111111111111)
        # return
        s.run()

    # def _save_chapter_db(self, comic_id, title):
    #     print(title, "<<<<<<<<<<<<<", comic_id)
    #     print(type(title), "<<<<<<<<<<<<<", type(comic_id))
    #     # chapter = Chapter.normal.filter(comic_id=comic_id, title=title).first()
    #     # if not chapter:
    #     chapter = Chapter()
    #     chapter.comic_id = comic_id
    #     chapter.title = title
    #     chapter.save()
    #     return chapter
