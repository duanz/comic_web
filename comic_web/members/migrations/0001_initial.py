# Generated by Django 2.0.13 on 2020-03-13 03:53

from django.db import migrations, models
import django.db.models.manager
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MemberViewHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_id', models.IntegerField(default=0, verbose_name='用户ID')),
                ('data_type', models.CharField(choices=[('BOOK', '小说'), ('COMIC', '漫画')], default='BOOK', max_length=10, verbose_name='数据类型')),
                ('title', models.CharField(default='', max_length=15, verbose_name='主题')),
                ('chapter_title', models.CharField(default='', max_length=15, verbose_name='章节主题')),
                ('active', models.BooleanField(default=True, verbose_name='是否生效')),
                ('content_id', models.IntegerField(default=0, verbose_name='主题ID')),
                ('chapter_id', models.IntegerField(default=0, verbose_name='章节ID')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('task_type', models.CharField(choices=[('BOOK_INSERT', '新增小说'), ('BOOK_CHAPTER_UPDATE', '更新小说章节'), ('COMIC_INSERT', '新增漫画'), ('COMIC_CHAPTER_UPDATE', '更新漫画章节')], default='BOOK_INSERT', max_length=10, verbose_name='任务类型')),
                ('active', models.BooleanField(default=False, verbose_name='是否生效')),
                ('user_id', models.IntegerField(default=0, verbose_name='下发任务用户ID')),
                ('task_status', models.CharField(choices=[('WAIT', '等待执行'), ('RUNNING', '执行中'), ('FINISH', '执行结束'), ('FAILD', '执行失败')], default='WAIT', max_length=10, verbose_name='任务状态')),
                ('content', models.CharField(default='', max_length=300, verbose_name='任务内容')),
                ('markup', models.CharField(default='', max_length=50, verbose_name='任务备注')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
    ]
