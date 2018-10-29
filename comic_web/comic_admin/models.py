from djongo import models
from comic_web.utils.common_data import GENDER_CHOICES
from comic_web.utils.base_model import BaseModel
import django.utils.timezone as timezone
import datetime


class Comic(BaseModel):
    title = models.CharField('漫画名称', max_length=100, default='')
    author_id = models.CharField('作者ID', max_length=30, default='')
    collection_num = models.IntegerField('收藏数量', null=True, default=0)
    click_num = models.IntegerField('点击数量', null=True, default=0)
    desc = models.CharField('描述', max_length=500, default="")
    markup = models.CharField('标签', null=True, max_length=100, default='')
    on_shelf = models.BooleanField('是否上架', default=True)

    class Meta:
        db_table = 'comic'
        ordering = ['-update_at']
        permissions = (
            ('comic_add', '添加漫画'),
            ('comic_edit', '编辑漫画'),
            ('comic_detail', '查看漫画'),
            ('comic_delete', '删除漫画'),
        )
