from django.contrib import admin

# Register your models here.
from .models import Task, Member


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_type', 'task_status', 'content')


# @admin.register(Member)
# class MemberAdmin(admin.ModelAdmin):
#     list_display = ('id', 'username', 'markup')
