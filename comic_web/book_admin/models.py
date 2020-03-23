# import datetime
from django.db import models
from comic_admin.models import Author

from comic_web.utils.base_model import BaseModel


# 小说表
class Book(BaseModel):
    title = models.CharField('小说名称', max_length=60, default='', unique=True)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    collection_num = models.IntegerField('收藏数量', null=True, default=0)
    click_num = models.IntegerField('点击数量', null=True, default=0)
    desc = models.CharField('描述', max_length=500, default="")
    markup = models.CharField('标签', null=True, max_length=100, default='')
    on_shelf = models.BooleanField('是否上架', default=True)
    is_download = models.BooleanField('是否可以下载', default=False)
    is_finished = models.BooleanField('是否能已完结', default=False)
    latest_chapter = models.CharField('最新章节', max_length=20, default="")
    origin_addr = models.CharField('原始地址', max_length=200, default="")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '小说'
        db_table = 'book'
        ordering = ['-update_at']
        permissions = (
            ('book_add', '添加小说'),
            ('book_edit', '编辑小说'),
            ('book_detail', '查看小说'),
            ('book_delete', '删除小说'),
        )


class Chapter(BaseModel):
    '''小说章节表'''
    book_id = models.IntegerField("小说ID", null=False, default=0)
    title = models.CharField('章节标题', null=False, max_length=60, default="")
    content = models.CharField('章节内容', null=False, max_length=10000, default="")
    number = models.IntegerField('章节编号', default=0)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)
    origin_addr = models.CharField('原始地址', max_length=200, default="")

    class Meta:
        verbose_name_plural = '章节'
        db_table = 'book_chapter'
        ordering = ['order', '-update_at']
        permissions = (
            ('book_chapter_add', '添加小说章节'),
            ('book_chapter_edit', '编辑小说章节'),
            ('book_chapter_detail', '查看小说章节'),
            ('book_chapter_delete', '删除小说章节'),
        )

    def __str__(self):
        return self.title
