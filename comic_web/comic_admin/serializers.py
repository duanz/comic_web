import os
import copy
from rest_framework import serializers
from comic_admin import models as ComicAdminModels
from book_admin import models as BookAdminModels
from book_admin import serializers as BookAdminSerializers
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
    path = serializers.SerializerMethodField()

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

    def get_path(self, obj):
        quality = self.context.get('quality', "")
        if quality == "thumb":
            url = photo_lib.build_photo_path(obj.key, pic_type="thumb")
        elif quality == "title":
            url = photo_lib.build_photo_path(obj.key, pic_type="title")
        return url


class ChapterSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    update_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.Chapter
        fields = ('__all__')


class ChapterDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    image_url_list = serializers.SerializerMethodField()
    relate_chapter_id = serializers.SerializerMethodField()
    comic_title = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Chapter
        fields = ("id", "comic_id", "title", "number", "order", "active", "create_at",
                  "origin_addr", "image_url_list", "relate_chapter_id", "comic_title")

    def get_comic_title(self, obj):
        comic_obj = ComicAdminModels.Comic.normal.filter(
            id=obj.comic_id).first()
        return comic_obj.title

    def get_image_url_list(self, obj):
        return CommonImageSerializer.to_representation(chapter_id=obj.id, quality="title", only_url=True)

    def get_relate_chapter_id(self, obj):
        query_set = ComicAdminModels.Chapter.normal.filter(
            comic_id=obj.comic_id).values("id")
        id_list = [item['id'] for item in query_set] if query_set else []
        index = id_list.index(obj.id)
        if index == 0:
            next_id = id_list[1] if len(id_list) >= 2 else id_list[0]
            pre_id = id_list[0]
        elif index == len(id_list) - 1:
            next_id = id_list[0]
            pre_id = id_list[index - 1]
        else:
            next_id = id_list[index + 1]
            pre_id = id_list[index - 1]

        return {"pre_id": pre_id, "next_id": next_id}


class CommonImageSerializer:

    @staticmethod
    def to_representation(comic_id=None, book_id=None, chapter_id=None, img_type="chapter_content", quality="thumb", only_url=True, only_path=False):
        if comic_id:
            comic_id_list = comic_id if isinstance(
                comic_id, list) else [comic_id]
        elif book_id:
            book_id_list = book_id if isinstance(book_id, list) else [book_id]
        elif chapter_id:
            chapter_id_list = chapter_id if isinstance(
                chapter_id, list) else [chapter_id]

        if img_type == "chapter_content":
            queryset = ComicAdminModels.ChapterImage.normal.filter(
                chapter_id__in=chapter_id_list, active=True).values("image_id")
        elif img_type == "chapter_cover":
            queryset = ComicAdminModels.CoverImage.normal.filter(
                chapter_id__in=chapter_id_list, active=True).values("image_id")
        elif img_type == "comic_cover":
            queryset = ComicAdminModels.CoverImage.normal.filter(
                comic_id__in=comic_id_list, active=True).values("image_id")
        elif img_type == "book_cover":
            queryset = ComicAdminModels.CoverImage.normal.filter(
                book_id__in=book_id_list, active=True).values("image_id")

        image_set = ComicAdminModels.Image.normal.filter(
            pk__in=[item.get("image_id") for item in queryset] if queryset else [])
        img_set = image_set.values('key')
        if only_url:
            if quality == "thumb":
                img_url_list = [photo_lib.get_thumb_img_url(
                    item) for item in img_set] if img_set else []
            elif quality == "title":
                img_url_list = [photo_lib.get_title_img_url(
                    item) for item in img_set] if img_set else []
            return img_url_list
        elif only_path:
            return [photo_lib.build_photo_path(item.get('key'), pic_type=quality) for item in img_set] if img_set else []
        else:
            serializer = ImageSerializer(
                image_set, many=True, context={"quality": quality})
            return serializer.data


class ComicSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    cover = serializers.SerializerMethodField()
    update_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    author = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Comic
        fields = ("id", "create_at", "status", "update_at", "title",
                  "collection_num", "click_num", "desc", "markup", "on_shelf", "is_download",
                  "is_finished", "author", "latest_chapter", "cover", "download_url", )
        read_only_fields = ("cover", "download_url", "is_download", )

    def get_cover(self, obj):
        return CommonImageSerializer.to_representation(comic_id=obj.id, img_type="comic_cover", quality="title")
    
    def get_author(self, obj):
        return str(obj.author)
    
    def get_download_url(self, obj):
        path = ""
        if obj.is_download:
            path = settings.APP_HOST + os.path.join(settings.UPLOAD_STATIC_URL, obj.title+'.docx')
        return path


class ComicDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    author = AuthorSerializer(read_only=True)
    chapter = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()
    update_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

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
        return CommonImageSerializer.to_representation(comic_id=obj.id, img_type="comic_cover", quality="title", only_url=False)


class SpydersUtilsSerializer(serializers.Serializer):
    def to_representation(self):
        def run_subprocess(url):
            task_type = "export_invite_stat"
            manage_path = os.path.join(settings.BASE_DIR, 'manage.py')
            subprocess.Popen(['python', manage_path, task_type, "-u", url])

        # run_subprocess("https://manhua.dmzj.com/zuixihuanderenwangjidaiyanjle/")
        run_subprocess("https://manhua.dmzj.com/nogunslife/")


class IndexBlockSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.IndexBlock
        fields = ('__all__')


class DefaultIndexSerializer(serializers.Serializer):

    def to_representation(self, index_type="comic"):
        data = {}
        if index_type == "comic":
            data = self.comic_index_block()
        elif index_type == "book":
            data = self.book_index_block()
        return data

    def get_index_carousel(self, queryset, comic_list):
        content_id_list = []
        for item in queryset:
            if item.desc_type == ComicAdminModels.INDEX_BLOCK_DESC.Carousel:
                content_id_list.append(item.content_id)
        res = []
        for i_id in content_id_list:
            for item in comic_list:
                if item['id'] == i_id:
                    item['url'] = item.get(
                        'cover')[0] if item.get('cover') else ""
                    res.append(item)
        return res

    def get_index_left(self, content_id, comic_list):
        for item in comic_list:
            if item.get('id') == content_id:
                temp = copy.deepcopy(item)
                temp['url'] = item.get('cover')[0] if item.get('cover') else ""
                temp['desc_type'] = ComicAdminModels.INDEX_BLOCK_DESC.Photo_Left
                return temp

    def get_index_top(self, content_id, comic_list):
        for item in comic_list:
            if item.get('id') == content_id:
                temp = copy.deepcopy(item)
                temp['url'] = item.get('cover')[0] if item.get('cover') else ""
                temp['desc_type'] = ComicAdminModels.INDEX_BLOCK_DESC.Photo_Top
                return temp

    def comic_index_block(self):
        queryset = ComicAdminModels.IndexBlock.normal.filter(
            block_type=ComicAdminModels.INDEX_BLOCK_TYPE_DESC.Comic)

        comic_id_list = [
            item.content_id for item in queryset] if queryset else []
        comic_objs = ComicAdminModels.Comic.normal.filter(id__in=comic_id_list)
        comic_list = ComicSerializer(comic_objs, many=True).data

        data = []
        data.append({'block_type': 'carousel',
                     'results': self.get_index_carousel(queryset, comic_list)})
        for item in queryset:
            temp_data = {}
            if item.desc_type == ComicAdminModels.INDEX_BLOCK_DESC.Photo_Left:
                temp_data = {'block_type': 'photo_left', 'results': self.get_index_left(
                    item.content_id, comic_list)}
            elif item.desc_type == ComicAdminModels.INDEX_BLOCK_DESC.Photo_Top:
                temp_data = {'block_type': 'photo_top', 'results': self.get_index_top(
                    item.content_id, comic_list)}

            if temp_data:
                data.append(temp_data)

        return data

    def book_index_block(self):
        queryset = ComicAdminModels.IndexBlock.normal.filter(
            block_type=ComicAdminModels.INDEX_BLOCK_TYPE_DESC.Book)

        book_id_list = [
            item.content_id for item in queryset] if queryset else []
        book_objs = BookAdminModels.Book.normal.filter(id__in=book_id_list)
        book_list = BookAdminSerializers.BookSerializer(
            book_objs, many=True).data

        data = []
        data.append({'block_type': 'carousel',
                     'results': self.get_index_carousel(queryset, book_list)})
        for item in queryset:
            temp_data = {}
            if item.desc_type == ComicAdminModels.INDEX_BLOCK_DESC.Photo_Left:
                temp_data = {'block_type': 'photo_left', 'results': self.get_index_left(
                    item.content_id, book_list)}
            elif item.desc_type == ComicAdminModels.INDEX_BLOCK_DESC.Photo_Top:
                temp_data = {'block_type': 'photo_top', 'results': self.get_index_top(
                    item.content_id, book_list)}

            if temp_data:
                data.append(temp_data)

        return data
