from __future__ import absolute_import, unicode_literals
import logging
from members import models as MemberModels
from comic_web.workers.spiders.tools import parser_selector
from comic_web.workers.spiders.bookSheduler import BookSheduler
from comic_web.workers.spiders.bookSheduler import BookChapterSheduler
from comic_web.workers.spiders.comicSheduler import ComicSheduler
from comic_web.workers.spiders.comicSheduler import ComicChapterSheduler


FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel('info'.upper())


def get_queryset():
    return MemberModels.Task.normal.filter(active=True, task_status=MemberModels.TASK_STATUS_DESC.WAIT)


def task():
    '''处理任务'''
    
    logging.info("任务开始执行！")
    queryset = get_queryset()
    logging.info("获取任务列表成功：共{}条".format(queryset.count()))
    for task in queryset:
        task.task_status = MemberModels.TASK_STATUS_DESC.RUNNING
        task.markup = ""
        task.save()

        if task.task_type in [MemberModels.TASK_TYPE_DESC.BOOK_INSERT, MemberModels.TASK_TYPE_DESC.BOOK_CHAPTER_UPDATE, MemberModels.TASK_TYPE_DESC.COMIC_INSERT, MemberModels.TASK_TYPE_DESC.COMIC_CHAPTER_UPDATE]:

            if task.task_type == MemberModels.TASK_TYPE_DESC.BOOK_INSERT:
                headers = {"referer": task.content}
                s = BookSheduler(
                    url=task.content,
                    header=headers,
                    parser=parser_selector.get_parser(task.content),
                    fetch_only=False,
                    verify_ssl=False)
            elif task.task_type == MemberModels.TASK_TYPE_DESC.BOOK_CHAPTER_UPDATE:
                content_dict = eval(task.content)
                s = BookChapterSheduler(
                    url=content_dict['url'],
                    book_id=content_dict['book_id'],
                    chapter_id=content_dict['chapter_id'],
                    parser=parser_selector.get_parser(content_dict['url'])
                )
            elif task.task_type == MemberModels.TASK_TYPE_DESC.COMIC_INSERT:
                headers = {"referer": task.content}
                s = ComicSheduler(
                    url=task.content,
                    header=headers,
                    parser=parser_selector.get_parser(task.content),
                    fetch_only=False,
                    verify_ssl=False
                )
            elif task.task_type == MemberModels.TASK_TYPE_DESC.COMIC_CHAPTER_UPDATE:
                content_dict = eval(task.content)
                s = ComicChapterSheduler(
                    url=content_dict['url'],
                    comic_id=content_dict['comic_id'],
                    chapter_id=content_dict['chapter_id'],
                    parser=parser_selector.get_parser(content_dict['url'])
                )

            try:
                s.run()
                pass
            except Exception as e:
                error_info = "执行任务失败： {}".format(e)
                logging.error(error_info)
                task.markup = error_info
                task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
                task.save()
                return

            task.task_status = MemberModels.TASK_STATUS_DESC.FINISH
            task.save()
            logging.error("执行任务结束")
            return

        else:
            task.task_status = MemberModels.TASK_STATUS_DESC.FAILD
            task.markup = "任务未执行， {}不存在".format(task.task_type)
            task.save()
            return


