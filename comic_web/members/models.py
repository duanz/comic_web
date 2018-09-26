from djongo import models
from django.contrib.auth.models import AbstractUser
from comic_web.utils.common_data import GENDER_CHOICES
from comic_web.utils.base_model import BaseModel
import django.utils.timezone as timezone
import datetime


class Member(AbstractUser, BaseModel):
    open_id = models.CharField(null=True, max_length=30)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    group_id = models.IntegerField(null=False, default=-1)
    inviter_id = models.IntegerField(null=True, default=-1)
    markup = models.CharField(null=True, max_length=30, default='')
    phone = models.CharField(null=True, max_length=30, default='')
    avatar_url = models.CharField(null=True, max_length=250, default='')
    share_qrcode_key = models.CharField(null=True, max_length=100, default='')

    class Meta:
        permissions = (
            ('member_list', '查看管理员列表'),
            ('member_add', '添加管理员'),
            ('member_edit', '编辑管理员'),
            ('member_detail', '查看管理员详情'),
            ('member_delete', '删除管理员'),

            ('group_list', '查看管理员组列表'),
            ('group_add', '添加管理员组'),
            ('group_edit', '编辑管理员组'),
            ('group_permission', '设置管理员组权限'),
            ('group_delete', '删除管理员组'),

            ('customer_list', '查看用户列表'),
            ('customer_detail', '查看用户详情'),
        )
