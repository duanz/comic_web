from django.contrib import admin
from comic_admin.models import Author, Comic, Chapter, Image
# Register your models here.

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile_phone')


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author_id', 'collection_num', 'click_num', 'desc', 'markup', 'on_shelf', 'is_finished', 'cover_img_list')


@admin.register(Author)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'comic_id', 'title', 'cover_img_id', 'order', 'active')


@admin.register(Author)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'key', 'img_type', 'order', 'active', 'chapter_id')
