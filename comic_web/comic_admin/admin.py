from django.contrib import admin
from django.utils.safestring import mark_safe
from comic_admin.models import Author, Comic, Chapter, Image
from comic_web.utils import photo as photo_lib
# Register your models here.

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile_phone')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'key', 'img_type', 'order', 'active', 'image_data')
    readonly_fields = ('image_data', )

    def image_data(self, obj):
        img_url = photo_lib.get_thumbicon_img_url(obj)
        return mark_safe('<img src="/%s" width="100px" />' % obj.image.url)
        # return '123'
    
    image_data.short_description = u'品牌图片'


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author_id', 'collection_num', 'click_num', 'desc', 'markup', 'on_shelf', 'is_finished')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'comic_id', 'title', 'order', 'active')

