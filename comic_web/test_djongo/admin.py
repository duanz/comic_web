from django.contrib import admin

# Register your models here.
from test_djongo.models import Blog, Entry

#Blog模型的管理器
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

#Blog模型的管理器


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'meta_data', 'authors')

    #Blog模型的管理器
