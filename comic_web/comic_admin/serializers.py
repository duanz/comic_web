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


class CoverImageSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.CoverImage
        fields = ('__all__')


class ImageSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    url = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Image
        fields = ('__all__')
    
    def get_url(self, obj):
        quality = self.context.get('quality', "")
        if quality == "thumb":
            url = photo_lib.get_thumb_img_url(obj)
        elif quality == "title":
            url = photo_lib.get_title_img_url(obj)
        return url


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
    relate_chapter_id = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Chapter
        fields = ("comic_id", "title", "number", "order", "active", "create_at", 
                  "origin_addr", "image_url_list", "relate_chapter_id")

    def get_image_url_list(self, obj):
        return CommonImageSerializer.to_representation(chapter_id=obj.id, quality="title", only_url=True)
    
    def get_relate_chapter_id(self, obj):
        query_set = ComicAdminModels.Chapter.normal.filter(comic_id=obj.comic_id).values("id")
        id_list = [item['id'] for item in query_set] if query_set else []
        index = id_list.index(obj.id)
        if index == 0:
            return {"pre_id": 0, "next_id": id_list[1]}
        elif index == len(id_list) - 1:
            return {"pre_id": index - 1, "next_id": 0}
        else:
            return {"pre_id": index - 1, "next_id": index + 1}





class CommonImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComicAdminModels.Image
        fields = ('__all__')

    def to_representation(comic_id=None, chapter_id=None, img_type="chapter_content", quality="thumb", only_url=True):
        if img_type == "chapter_content":
            queryset = ComicAdminModels.ChapterImage.normal.filter(chapter_id=chapter_id, active=True).values("image_id")
        elif img_type == "chapter_cover":
            queryset = ComicAdminModels.CoverImage.normal.filter(chapter_id=chapter_id, active=True).values("image_id")
        elif img_type == "comic_cover":
            queryset = ComicAdminModels.CoverImage.normal.filter(comic_id=comic_id, active=True).values("image_id")
        
        if only_url:
            img_set = ComicAdminModels.Image.normal.filter(pk__in=[item.get("image_id") for item in queryset] if queryset else []).values('key')
            if quality == "thumb":
                img_url_list = [photo_lib.get_thumb_img_url(item) for item in img_set] if img_set else []
            elif quality == "title":
                img_url_list = [photo_lib.get_title_img_url(item) for item in img_set] if img_set else []
            return img_url_list
        else:
            image_set = ComicAdminModels.Image.normal.filter(pk__in=[item.get("image_id") for item in queryset] if queryset else [])
            serializer = ImageSerializer(image_set, many=True, context={"quality": quality})
            return serializer.data


class ComicSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    cover = serializers.SerializerMethodField()
        
    class Meta:
        model = ComicAdminModels.Comic
        fields = ("id", "create_at", "status", "update_at", "title",
                  "collection_num", "click_num", "desc", "markup", "on_shelf",
                  "is_finished", "author", "latest_chapter", "cover")
        read_only_fields = ("cover", )

    def get_cover(self, obj):
        return CommonImageSerializer.to_representation(comic_id=obj.id, img_type="comic_cover")


class ComicDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    author = AuthorSerializer(read_only=True)
    chapter = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Comic
        fields = ("id", "create_at", "status", "update_at", "title",
                  "collection_num", "click_num", "desc", "markup", "on_shelf",
                  "is_finished", "author", "latest_chapter", "chapter", "cover")

        read_only_fields = ("chapter", "cover")

    def get_chapter(self, obj):
        chapters = ComicAdminModels.Chapter.normal.filter(comic_id=obj.id)
        return ChapterSerializer(chapters, many=True).data
    
    def get_cover(self, obj):
        return CommonImageSerializer.to_representation(comic_id=obj.id, img_type="comic_cover", only_url=False)


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
