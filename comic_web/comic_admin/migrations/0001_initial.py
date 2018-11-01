# Generated by Django 2.1.2 on 2018-11-01 07:51

import comic_web.utils.photo
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(default='anonymous', max_length=60, verbose_name='作者名')),
                ('mobile_phone', models.CharField(default='', max_length=20, verbose_name='手机号')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(default='', max_length=60, verbose_name='章节标题')),
                ('order', models.IntegerField(default=0, verbose_name='排序位置')),
                ('active', models.BooleanField(default=True, verbose_name='生效')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ChapterImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('chapter_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Chapter')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Comic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(default='', max_length=60, unique=True, verbose_name='漫画名称')),
                ('collection_num', models.IntegerField(default=0, null=True, verbose_name='收藏数量')),
                ('click_num', models.IntegerField(default=0, null=True, verbose_name='点击数量')),
                ('desc', models.CharField(default='', max_length=500, verbose_name='描述')),
                ('markup', models.CharField(default='', max_length=100, null=True, verbose_name='标签')),
                ('on_shelf', models.BooleanField(default=True, verbose_name='是否上架')),
                ('is_finished', models.BooleanField(default=False, verbose_name='是否能已完结')),
                ('author_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Author')),
            ],
            options={
                'db_table': 'comic',
                'ordering': ['-update_at'],
                'permissions': (('comic_add', '添加漫画'), ('comic_edit', '编辑漫画'), ('comic_detail', '查看漫画'), ('comic_delete', '删除漫画')),
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='CoverImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('chapter_id', models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Chapter')),
                ('comic_id', models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Comic')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='normal', max_length=10)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('img_type', models.CharField(choices=[('0', '漫画封面'), ('1', '章节封面'), ('2', '章节内容')], default='', max_length=2, null=True, verbose_name='图片类型')),
                ('order', models.IntegerField(default=0, verbose_name='排序位置')),
                ('active', models.BooleanField(default=True, verbose_name='生效')),
                ('name', models.CharField(default='', max_length=255, verbose_name='名称')),
                ('key', models.ImageField(blank=True, unique=True, upload_to=comic_web.utils.photo.django_image_upload_handler, verbose_name='图片')),
            ],
            options={
                'db_table': 'comic_image',
                'ordering': ['order'],
            },
            managers=[
                ('normal', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='coverimage',
            name='img_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Image'),
        ),
        migrations.AddField(
            model_name='comic',
            name='cover_image',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, related_name='comic_cover_image', to='comic_admin.Image', to_field='key'),
        ),
        migrations.AddField(
            model_name='chapterimage',
            name='comic_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Comic'),
        ),
        migrations.AddField(
            model_name='chapterimage',
            name='img_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Image'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='comic_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='comic_admin.Comic'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='cover_image',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, related_name='chapter_cover_image', to='comic_admin.Image', to_field='key'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='detail_image',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, related_name='chapter_detail_image', to='comic_admin.Image', to_field='key'),
        ),
    ]
