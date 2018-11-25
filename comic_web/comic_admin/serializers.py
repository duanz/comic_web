# import sys, os
# current_directory = os.path.dirname(os.path.abspath(__file__))
# root_path = os.path.abspath(
#     os.path.dirname(current_directory) + os.path.sep + ".")
# sys.path.append(root_path)
# print(sys.path)
from rest_framework import serializers
from comic_admin import models as ComicAdminModels
import subprocess
from django.conf import settings
from comic_web.utils import photo as photo_lib


class AuthorSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.Author
        fields = ('__all__')


class ImageSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.Image
        fields = ('__all__')


class ChapterSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.Chapter
        fields = ('__all__')


class ChapterDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    image_url_list = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Chapter
        fields = ("comic_id", "title", "number", "order", "active", "create_at", 
                  "origin_addr", "image_url_list")

    def get_image_url_list(self, obj):
        return ChapterImageSerializer.to_representation(obj.id)


class ChapterImageSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.ChapterImage
        fields = ('__all__')

    def to_representation(chapter_id):
        queryset = ComicAdminModels.ChapterImage.normal.filter(chapter_id=chapter_id).values("image_id")
        img_set = ComicAdminModels.Image.normal.filter(
            pk__in=[item.get("image_id") for item in queryset] if queryset else []).values('key')
        img_url_list = [photo_lib.get_thumb_img_url(item) for item in img_set] if img_set else []
        return img_url_list


class ComicSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.Comic
        fields = ('__all__')


class ComicDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    author = AuthorSerializer(read_only=True)
    chapter = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Comic
        fields = ("id", "create_at", "status", "update_at", "title",
                  "collection_num", "click_num", "desc", "markup", "on_shelf",
                  "is_finished", "author", "chapter")

        read_only_fields = ("chapter", )

    def get_chapter(self, obj):
        chapters = ComicAdminModels.Chapter.normal.filter(comic_id=obj.id)
        return ChapterSerializer(chapters, many=True).data


import os


class SpydersUtilsSerializer(serializers.Serializer):
    def to_representation(self):
        # subprocess.Popen([
        #     "python",
        #     # "E:\\myProjcet\\com_comic_web\\comic_we\\workers\\comic_spiders\\main.py",
        #     "E:\\myProjcet\\com_comic_web\\comic_web\\comic_web\\workers\\comic_spiders\\main.py",
        #     # "python",
        #     "https://manhua.dmzj.com/yiquanchaoren/"
        # ])

        def run_subprocess(url):
            task_type = "export_invite_stat"
            manage_path = os.path.join(settings.BASE_DIR, 'manage.py')
            subprocess.Popen(['python', manage_path, task_type, "-u", url])

        run_subprocess(
            "https://manhua.dmzj.com/zuixihuanderenwangjidaiyanjle/")
