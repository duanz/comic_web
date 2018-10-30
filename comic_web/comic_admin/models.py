from djongo import models
from comic_web.utils.common_data import GENDER_CHOICES
from comic_web.utils.base_model import BaseModel
import django.utils.timezone as timezone
import datetime


class IMAGE_TYPE_DESC:
    COMIC_COVER = '0'
    CHAPTER_COVER = '1'
    CHAPER_CONTENT = '2'


IMAGE_TYPE = (
    (IMAGE_TYPE_DESC.COMIC_COVER, '漫画封面'),
    (IMAGE_TYPE_DESC.CHAPTER_COVER, '章节封面'),
    (IMAGE_TYPE_DESC.CHAPER_CONTENT, '章节内容'),
)


class Author(BaseModel):
    name = models.CharField('作者名', max_length=60, default="anonymous")
    mobile_phone = models.IntegerField("手机号", default=0)


# 漫画表
class Comic(BaseModel):
    title = models.CharField('漫画名称', max_length=60, default='', unique=True)
    author_id = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    collection_num = models.IntegerField('收藏数量', null=True, default=0)
    click_num = models.IntegerField('点击数量', null=True, default=0)
    desc = models.CharField('描述', max_length=500, default="")
    markup = models.CharField('标签', null=True, max_length=100, default='')
    on_shelf = models.BooleanField('是否上架', default=True)
    is_finished = models.BooleanField('是否能已完结', default=False)
    cover_img_list = models.ManyToManyField(Image, default=0)

    class Meta:
        db_table = 'comic'
        ordering = ['-update_at']
        permissions = (
            ('comic_add', '添加漫画'),
            ('comic_edit', '编辑漫画'),
            ('comic_detail', '查看漫画'),
            ('comic_delete', '删除漫画'),
        )

# 漫画章节表
class Chapter(BaseModel):
    comic_id = models.ForeignKey(Comic, on_delete=models.DO_NOTHING)
    title = models.CharField('章节标题', null=False, max_length=60, default="")
    cover_img_id = models.ForeignKey(Image, default=0, null=True, on_delete=models.DO_NOTHING)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)


class Image(BaseModel):
    """图片"""
    key = models.CharField('图片文件名', null=True, max_length=100, default='')
    img_type = models.CharField('图片类型', null=True, max_length=2, default='', choices=IMAGE_TYPE)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)
    name = models.CharField('名称', max_length=255, default='')
    chapter_id = models.ForeignKey(Chapter, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'comic_image'
        ordering = ['order']








