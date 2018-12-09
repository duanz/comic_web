from django.contrib import admin
from django.utils.safestring import mark_safe
from comic_web.utils import photo as photo_lib
from book_admin.models import Book, Chapter
# # Register your models here.


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_id', 'title', 'order', 'active')
