from django.db import models

# from django.contrib.auth.models import AbstractUser
from comic_web.utils.base_model import BaseModel


class HISTORY_DATA_TYPE_DESC:
    BOOK = "BOOK"
    COMIC = "COMIC"


class TASK_TYPE_DESC:
    BOOK_INSERT = "BOOK_INSERT"
    BOOK_CHAPTER_UPDATE = "BOOK_CHAPTER_UPDATE"
    COMIC_INSERT = "COMIC_INSERT"
    COMIC_CHAPTER_UPDATE = "COMIC_CHAPTER_UPDATE"


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
)

TASK_STATUS = (
    (TASK_STATUS_DESC.WAIT, "等待执行"),
    (TASK_STATUS_DESC.RUNNING, "执行中"),
    (TASK_STATUS_DESC.FINISH, "执行结束"),
    (TASK_STATUS_DESC.FAILD, "执行失败"),
)


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


# class Member(BaseModel):
#     open_id = models.CharField(null=True, max_length=30)
#     gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
#     group_id = models.IntegerField(null=False, default=-1)
#     inviter_id = models.IntegerField(null=True, default=0)
#     markup = models.CharField(null=True, max_length=30, default='')
#     phone = models.CharField(null=True, max_length=30, default='')
#     avatar_url = models.CharField(null=True, max_length=250, default='')

#     class Meta:
#         permissions = (
#             ('member_list', '查看管理员列表'),
#             ('member_add', '添加管理员'),
#             ('member_edit', '编辑管理员'),
#             ('member_detail', '查看管理员详情'),
#             ('member_delete', '删除管理员'),

#             ('group_list', '查看管理员组列表'),
#             ('group_add', '添加管理员组'),
#             ('group_edit', '编辑管理员组'),
#             ('group_permission', '设置管理员组权限'),
#             ('group_delete', '删除管理员组'),

#             ('customer_list', '查看用户列表'),
#             ('customer_detail', '查看用户详情'),
#         )
