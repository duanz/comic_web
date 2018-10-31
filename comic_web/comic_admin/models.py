import datetime
from djongo import models
from comic_web.utils.common_data import GENDER_CHOICES
from comic_web.utils.base_model import BaseModel
from comic_web.utils import photo as photo_lib
import django.utils.timezone as timezone


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
    mobile_phone = models.CharField("手机号", default="", max_length=20)

    def __str__(self):
        return self.name


class Image(BaseModel):
    """图片"""
    img_type = models.CharField('图片类型', null=True, max_length=2, default='', choices=IMAGE_TYPE)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)
    name = models.CharField('名称', max_length=255, default='')
    key = models.ImageField('图片', upload_to=photo_lib.django_image_upload_handler, blank=True)

    class Meta:
        db_table = 'comic_image'
        ordering = ['order']


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

    def __str__(self):
        return self.title

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
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)

    def __str__(self):
        return self.title


class ChapterImage(BaseModel):
    '''章节图片中间表'''
    comic_id = models.ForeignKey(Comic, default=0, on_delete=models.DO_NOTHING)
    chapter_id = models.ForeignKey(Chapter, default=0, on_delete=models.DO_NOTHING)
    img_id = models.ForeignKey(Image, default=0, on_delete=models.DO_NOTHING)


class CoverImage(BaseModel):
    '''封面图片中间表'''
    comic_id = models.ForeignKey(Comic, default=0, on_delete=models.DO_NOTHING, null=True)
    chapter_id = models.ForeignKey(Chapter, default=0, null=True, on_delete=models.DO_NOTHING)
    img_id = models.ForeignKey(Image, default=0, on_delete=models.DO_NOTHING)
