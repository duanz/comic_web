from django.contrib import admin
# from django.utils.safestring import mark_safe
from comic_admin.models import Author, Comic, Chapter, Image, ChapterImage, CoverImage, IndexBlock
# from comic_web.utils import photo as photo_lib
# # Register your models here.

# admin.register(IndexBlock)
@admin.register(IndexBlock)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'block_type', 'desc_type', 'content_id')

# @admin.register(Author)
# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'mobile_phone')


# @admin.register(Image)
# class ImageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'key', 'img_type', 'order', 'active', 'image_data')
#     readonly_fields = ('image_data', )
#     list_filter = ('img_type', 'active',)
#     list_editable = ('img_type', 'active', 'name')
#     search_fields = ('name', )

#     def image_data(self, obj):
#         img_url = ""
#         if obj:
#             img_url = photo_lib.build_photo_url(str(obj.key), 'thumbicon')
#         return mark_safe('<img src="%s" style="max-width:50px" />' % img_url)
    
#     image_data.short_description = u'品牌图片'


# @admin.register(Comic)
# class ComicAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'author', 'collection_num', 'click_num', 'desc', 'markup', 'on_shelf', 'is_finished', 'cover_image_read')
#     readonly_fields = ('cover_image_read', )

#     def cover_image_read(self, obj):
#         all_cover_image_obj_list = CoverImage.normal.filter(comic_id=obj.id)

#         all_cover_image_id_list = [temp.id for temp in all_cover_image_obj_list] if all_cover_image_obj_list else []

#         all_cover_image_list = Image.normal.filter(id__in=all_cover_image_id_list)

#         html_str = "<ul style='display:inline-flex;'>{}</ul>"
#         li_str = "<li style='padding-right:3px;'><img src='{}' style='max-width: 50px' /></li>"
#         all_li = ""
#         for img in all_cover_image_list:
#             img_url = photo_lib.build_photo_url(str(img.key), "thumbicon")
#             all_li += li_str.format(img_url)
#         return mark_safe(html_str.format(all_li))
    
#     cover_image_read.short_description = '封面图片'


# @admin.register(Chapter)
# class ChapterAdmin(admin.ModelAdmin):
#     list_display = ('id', 'comic', 'title', 'order','active', 'cover_image_read', 'detail_image_read')

#     readonly_fields = ('cover_image_read', 'detail_image_read',)

#     def cover_image_read(self, obj):
#         all_cover_image_obj_list = CoverImage.normal.filter(chapter_id=obj.id)

#         all_cover_image_id_list = [ temp.id for temp in all_cover_image_obj_list ] if all_cover_image_obj_list else []

#         all_cover_image_list = Image.normal.filter(id__in=all_cover_image_id_list)

#         html_str = "<ul style='display:inline-flex;'>{}</ul>"
#         li_str = "<li style='padding-right:3px;'><img src='{}' style='max-width: 50px' /></li>"
#         all_li = ""
#         for img in all_cover_image_list:
#             img_url = photo_lib.build_photo_url(str(img.key), "thumbicon")
#             all_li += li_str.format(img_url)
#         return mark_safe(html_str.format(all_li))

#     def detail_image_read(self, obj):
#         all_cover_image_obj_list = ChapterImage.normal.filter(chapter_id=obj.id)

#         all_cover_image_id_list = [temp.id for temp in all_cover_image_obj_list] if all_cover_image_obj_list else []

#         all_cover_image_list = Image.normal.filter(
#             id__in=all_cover_image_id_list)

#         html_str = "<ul style='display:inline-flex;'>{}</ul>"
#         li_str = "<li style='padding-right:3px;'><img src='{}' style='max-width: 50px' /></li>"
#         all_li = ""
#         for img in all_cover_image_list:
#             img_url = photo_lib.build_photo_url(str(img.key), "thumbicon")
#             all_li += li_str.format(img_url)
#         return mark_safe(html_str.format(all_li))

#     cover_image_read.short_description = '封面图片'
#     detail_image_read.short_description = '详情图片'


# @admin.register(ChapterImage)
# class ChapterImageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'comic', 'chapter', 'order','active')


# @admin.register(CoverImage)
# class CoverImageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'comic', 'chapter', 'order', 'active')
#     list_filter = ("active", )
#     search_fields = ("comic_title", "chapter_title", )
