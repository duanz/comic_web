from djongo import models
# from django.contrib.auth.models import AbstractUser
from comic_web.utils.base_model import BaseModel
import django.utils.timezone as timezone
import datetime


class HISTORY_DATA_TYPE_DESC:
    BOOK = "BOOK",
    COMIC = "COMIC",


HISTORY_DATA_TYPE = (
    (HISTORY_DATA_TYPE_DESC.BOOK, "小说"),
    (HISTORY_DATA_TYPE_DESC.COMIC, "漫画"),
)


class MemberViewHistory(BaseModel):
    {'id': 1, 'data_type': 'book', 'title': '我不成仙',
     'chapter_id': 50, 'content_id': 1, 'chapter_title': '第50章 要上天吗'}

    user_id = models.IntegerField("用户ID", default=0)
    data_type = models.CharField(
        "数据类型", default="", max_length=10, choices=HISTORY_DATA_TYPE)
    title = models.CharField("主题", default="", max_length=15)
    chapter_title = models.CharField("章节主题", default="", max_length=15)
    content_id = models.IntegerField("主题ID", default=0)
    chapter_id = models.IntegerField("章节ID", default=0)

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
