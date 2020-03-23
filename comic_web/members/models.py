from django.contrib.auth.models import AbstractUser
from comic_web.utils.base_model import BaseModel
from django.db import models


class HISTORY_DATA_TYPE_DESC:
    BOOK = "BOOK"
    COMIC = "COMIC"


class TASK_TYPE_DESC:
    BOOK_INSERT = "BOOK_INSERT"
    BOOK_CHAPTER_UPDATE = "BOOK_CHAPTER_UPDATE"
    COMIC_INSERT = "COMIC_INSERT"
    COMIC_CHAPTER_UPDATE = "COMIC_CHAPTER_UPDATE"
    BOOK_MAKE_EPUB = "BOOK_MAKE_EPUB"
    COMIC_MAKE_EPUB = "COMIC_MAKE_EPUB"
    SEND_TO_KINDLE = "SEND_TO_KINDLE"


class TASK_STATUS_DESC:
    WAIT = "WAIT"
    RUNNING = "RUNNING"
    FINISH = "FINISH"
    FAILD = "FAILD"


HISTORY_DATA_TYPE = (
    (HISTORY_DATA_TYPE_DESC.BOOK, "小说"),
    (HISTORY_DATA_TYPE_DESC.COMIC, "漫画"),
)

TASK_TYPE = (
    (TASK_TYPE_DESC.BOOK_INSERT, "新增小说"),
    (TASK_TYPE_DESC.BOOK_CHAPTER_UPDATE, "更新小说章节"),
    (TASK_TYPE_DESC.COMIC_INSERT, "新增漫画"),
    (TASK_TYPE_DESC.COMIC_CHAPTER_UPDATE, "更新漫画章节"),
    (TASK_TYPE_DESC.COMIC_MAKE_EPUB, "制作漫画EPUB"),
    (TASK_TYPE_DESC.BOOK_MAKE_EPUB, "制作小说EPUB"),
    (TASK_TYPE_DESC.SEND_TO_KINDLE, "推送至Kindle")
)

TASK_STATUS = (
    (TASK_STATUS_DESC.WAIT, "等待执行"),
    (TASK_STATUS_DESC.RUNNING, "执行中"),
    (TASK_STATUS_DESC.FINISH, "执行结束"),
    (TASK_STATUS_DESC.FAILD, "执行失败"),
)

GENDER_CHOICES = (('M', '男'), ('F', '女'), ('U', '未知'))


class Member(AbstractUser, BaseModel):
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    group_id = models.IntegerField(null=False, default=-1)
    inviter_id = models.IntegerField(null=True, default=0)
    markup = models.CharField(null=True, max_length=300, default='')
    phone = models.CharField(null=True, max_length=30, default='')
    avatar_url = models.CharField(null=True, max_length=250, default='')


class MemberViewHistory(BaseModel):
    user_id = models.IntegerField("用户ID", default=0)
    data_type = models.CharField("数据类型", default=HISTORY_DATA_TYPE_DESC.BOOK, max_length=50, choices=HISTORY_DATA_TYPE)
    title = models.CharField("主题", default="", max_length=15)
    chapter_title = models.CharField("章节主题", default="", max_length=50)
    active = models.BooleanField("是否生效", default=True)
    content_id = models.IntegerField("主题ID", default=0)
    chapter_id = models.IntegerField("章节ID", default=0)


class Task(BaseModel):
    task_type = models.CharField("任务类型", default=TASK_TYPE_DESC.BOOK_INSERT, max_length=50, choices=TASK_TYPE)
    active = models.BooleanField("是否生效", default=False)
    user_id = models.IntegerField("下发任务用户ID", default=0)
    task_status = models.CharField("任务状态", default=TASK_STATUS_DESC.WAIT, max_length=50, choices=TASK_STATUS)
    content = models.CharField("任务内容", default="", max_length=300)
    markup = models.CharField("任务备注", default="", max_length=200)



