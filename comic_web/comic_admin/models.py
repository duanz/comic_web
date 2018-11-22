# import datetime
from djongo import models
from comic_web.utils.base_model import BaseModel
from comic_web.utils import photo as photo_lib
import django.utils.timezone as timezone
from django.utils.safestring import mark_safe


class GENDER_TYPE_DESC:
    Male = "M"
    Female = "F"
    Anonymous = "A"


class IMAGE_TYPE_DESC:
    COMIC_COVER = '0'
    CHAPTER_COVER = '1'
    CHAPER_CONTENT = '2'


GENDER_CHOICES = (
    (GENDER_TYPE_DESC.Male, '男'),
    (GENDER_TYPE_DESC.Female, '女'),
    (GENDER_TYPE_DESC.Anonymous, '未知')
)

IMAGE_TYPE = (
    (IMAGE_TYPE_DESC.COMIC_COVER, '漫画封面'),
    (IMAGE_TYPE_DESC.CHAPTER_COVER, '章节封面'),
    (IMAGE_TYPE_DESC.CHAPER_CONTENT, '章节内容'),
)


class Author(BaseModel):
    name = models.CharField('作者名', max_length=60, default="anonymous")
    gender = models.CharField(
        '性别', max_length=2, default="A", choices=GENDER_CHOICES)
    mobile_phone = models.CharField("手机号", default="", max_length=20)

    class Meta:
        verbose_name_plural = '作者'

    def __str__(self):
        return self.name


class Image(BaseModel):
    """图片"""
    img_type = models.CharField(
        '图片类型', null=True, max_length=2, default='', choices=IMAGE_TYPE)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)
    name = models.CharField('名称', max_length=255, default='')
    key = models.ImageField(
        '图片', upload_to=photo_lib.django_image_upload_handler, blank=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'comic_image'
        verbose_name_plural = '图片'
        ordering = ['order']


# 漫画表
class Comic(BaseModel):
    title = models.CharField('漫画名称', max_length=60, default='', unique=True)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    collection_num = models.IntegerField('收藏数量', null=True, default=0)
    click_num = models.IntegerField('点击数量', null=True, default=0)
    desc = models.CharField('描述', max_length=500, default="")
    markup = models.CharField('标签', null=True, max_length=100, default='')
    on_shelf = models.BooleanField('是否上架', default=True)
    is_finished = models.BooleanField('是否能已完结', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '漫画'
        db_table = 'comic'
        ordering = ['-update_at']
        permissions = (
            ('comic_add', '添加漫画'),
            ('comic_edit', '编辑漫画'),
            ('comic_detail', '查看漫画'),
            ('comic_delete', '删除漫画'),
        )


class Chapter(BaseModel):
    '''漫画章节表'''
    comic = models.ForeignKey(Comic, on_delete=models.DO_NOTHING)
    title = models.CharField('章节标题', null=False, max_length=60, default="")
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)

    class Meta:
        verbose_name_plural = '章节'

    def __str__(self):
        return self.title


class ChapterImage(BaseModel):
    '''章节图片中间表'''
    comic = models.ForeignKey(
        Comic, default=0, on_delete=models.DO_NOTHING, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.DO_NOTHING)
    image = models.ForeignKey(Image, limit_choices_to={"img_type__in": [
                              IMAGE_TYPE_DESC.CHAPER_CONTENT]}, default=0, on_delete=models.DO_NOTHING)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)

    class Meta:
        verbose_name_plural = '章节详情'


class CoverImage(BaseModel):
    '''封面图片中间表'''
    comic = models.ForeignKey(
        Comic, default=0, on_delete=models.DO_NOTHING, null=True)
    chapter = models.ForeignKey(
        Chapter, null=True, blank=True, on_delete=models.DO_NOTHING)
    image = models.ForeignKey(Image, limit_choices_to={"img_type__in": [
                              IMAGE_TYPE_DESC.COMIC_COVER, IMAGE_TYPE_DESC.CHAPTER_COVER]}, default=0, on_delete=models.DO_NOTHING)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)

    class Meta:
        verbose_name_plural = '封面'
