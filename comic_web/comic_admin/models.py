# import datetime
from djongo import models

from comic_web.utils.base_model import BaseModel


class GENDER_TYPE_DESC:
    Male = "M"
    Female = "F"
    Anonymous = "A"


class IMAGE_TYPE_DESC:
    COMIC_COVER = '0'
    CHAPTER_COVER = '1'
    CHAPER_CONTENT = '2'
    BOOK_COVER = '3'


class INDEX_BLOCK_DESC:
    Carousel = "CA"
    Photo_Left = "PL"
    Photo_Top = "PT"


class INDEX_BLOCK_TYPE_DESC:
    Comic = "COMIC"
    Book = "BOOK"


GENDER_CHOICES = ((GENDER_TYPE_DESC.Male, '男'), (GENDER_TYPE_DESC.Female, '女'),
                  (GENDER_TYPE_DESC.Anonymous, '未知'))

IMAGE_TYPE = (
    (IMAGE_TYPE_DESC.COMIC_COVER, '漫画封面'),
    (IMAGE_TYPE_DESC.BOOK_COVER, '小说封面'),
    (IMAGE_TYPE_DESC.CHAPTER_COVER, '章节封面'),
    (IMAGE_TYPE_DESC.CHAPER_CONTENT, '章节内容'),
)

BLOCK_DESC_CHOICES = (
    (INDEX_BLOCK_DESC.Carousel, "轮播图"),
    (INDEX_BLOCK_DESC.Photo_Left, "图片在左"),
    (INDEX_BLOCK_DESC.Photo_Top, "图片在上"),
)

BLOCK_TYPE_CHOICES = (
    (INDEX_BLOCK_TYPE_DESC.Comic, "漫画"),
    (INDEX_BLOCK_TYPE_DESC.Book, "小说"),
)


class Author(BaseModel):
    name = models.CharField('作者名', max_length=60, default="anonymous")
    gender = models.CharField('性别', max_length=2, default="A", choices=GENDER_CHOICES)
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
    key = models.CharField("图片ID KEY", max_length=30, default="")

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
    latest_chapter = models.CharField('最新章节', max_length=20, default="")
    origin_addr = models.CharField('原始地址', max_length=200, default="")

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
    comic_id = models.IntegerField("漫画ID", null=False, default=0)
    title = models.CharField('章节标题', null=False, max_length=60, default="")
    number = models.IntegerField('章节编号', default=0)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)
    origin_addr = models.CharField('原始地址', max_length=200, default="")

    class Meta:
        verbose_name_plural = '章节'
        db_table = 'comic_chapter'
        ordering = ['order', '-update_at']
        permissions = (
            ('comic_chapter_add', '添加漫画章节'),
            ('comic_chapter_edit', '编辑漫画章节'),
            ('comic_chapter_detail', '查看漫画章节'),
            ('comic_chapter_delete', '删除漫画章节'),
        )

    def __str__(self):
        return self.title


class ChapterImage(BaseModel):
    '''章节图片中间表'''
    comic_id = models.IntegerField("漫画ID", null=False, default=0)
    chapter_id = models.IntegerField("章节ID", null=False, default=0)
    image_id = models.IntegerField("图片ID", null=True, default=0)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)

    class Meta:
        verbose_name_plural = '章节详情'


class CoverImage(BaseModel):
    '''封面图片中间表'''
    comic_id = models.IntegerField("漫画ID", null=False, default=0)
    book_id = models.IntegerField("小说ID", null=False, default=0)
    chapter_id = models.IntegerField("章节ID", null=False, default=0)
    image_id = models.IntegerField("图片ID", null=True, default=0)
    order = models.IntegerField('排序位置', default=0)
    active = models.BooleanField('生效', default=True)

    class Meta:
        verbose_name_plural = '封面'


class IndexBlock(BaseModel):
    '''首页模块表'''
    block_type = models.CharField("模块类型", null=False, max_length=10, default="COMIC", choices=BLOCK_TYPE_CHOICES)
    desc_type = models.CharField("模块类型", null=False, max_length=10, default="CA", choices=BLOCK_DESC_CHOICES)
    content_id = models.IntegerField("内容ID", null=False, default=0)
