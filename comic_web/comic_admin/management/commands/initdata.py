import random
import time
from django.core.management.base import BaseCommand
from comic_admin import models as admin_models


class Command(BaseCommand):
    """
    插入数据，默认情况下创建：
        - 2个分类（父分类和子分类各一个）
        - 2张首页轮播图
        - 5个商品（同一套餐）
        - 1个首页商品组（包含上面创建的5个商品，样式为双列纵向浏览）
    参数：
        -g 指定创建商品个数
    """
    help = 'Load initial data for new project.'

    def add_arguments(self, parser):
        # 指定创建商品数
        parser.add_argument('-g', dest='goods_count', help='init goods count default is 5', type=int)
        parser.add_argument('-o', '--only-create-goods', help='init goods count default is 5')

    def handle(self, *args, **options):
        try:
            author = self.create_author()
            comic = self.create_comic(author)
            self.create_chapter(comic)
        except Exception as e:
            print(e)
            pass
        
        
        self.stdout.write(self.style.SUCCESS('Init Successfully.'))

    def create_images(self, img_type):
        # 添加图片
        _image = admin_models.Image.normal.create(**{
            "img_type": img_type,
            "active": True,
            "name": "11111111",
            "key": str(time.time()),
            "order": 0
        })
        return _image
    
    def create_author(self):
        _author = admin_models.Author.normal.create(**{
            "name": "duan",
            "mobile_phone": "18575563713"
        })
        return _author
    
    def create_comic(self, author):
        _comic = admin_models.Comic.normal.create(**{
            "title": "寻秦记",
            "author": author,
            "collection_num": 10,
            "click_num": 500,
            "desc": "a step into the past.",
            "markup": "穿越",
            "on_shelf": True,
            "is_finished": True
        })
        _image = self.create_images(admin_models.IMAGE_TYPE_DESC.COMIC_COVER)
        self.create_cover_image(_image, null, _comic)

        return _comic
    
    def create_chapter(self, comic):
        for i in range(10):
            _chapter = admin_models.Chapter.normal.cretae(**{
                "comic": comic,
                "title": f"第{i}章",
                "order": i,
                "active": True
            })
            cover_image = self.create_images(admin_models.IMAGE_TYPE_DESC.CHAPTER_COVER)
            self.create_cover_image(cover_image, _chapter, null)

            for j in range(3):
                chapter_image = self.create_images(admin_models.IMAGE_TYPE_DESC.CHAPER_CONTENT)
                self.create_chapter_image(chapter_image, _chapter, comic)


    def create_chapter_image(self, image, chapter, comic):
        _obj = admin_models.ChapterImage.normal.create(**{
            "comic": comic,
            "chapter": chapter,
            "image": image,
            "order": 0,
            "active": True,
        })
    
    def create_cover_image(self, image, chapter, comic):
        _obj = admin_models.CoverImage.normal.create(**{
            "comic": comic,
            "chapter": chapter,
            "image": image,
            "order": 0,
            "active": True,
        })
