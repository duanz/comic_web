import os
from rest_framework import serializers
from comic_admin import models as ComicAdminModels
from comic_admin import serializers as ComicAdminSerializers
from book_admin import models as BookAdminModels
import subprocess
from django.conf import settings


class ChapterSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = BookAdminModels.Chapter
        fields = ("id", "book_id", "title", "number", "order", "create_at", )


class ChapterDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    relate_chapter_id = serializers.SerializerMethodField()
    book_title = serializers.SerializerMethodField()

    class Meta:
        model = BookAdminModels.Chapter
        fields = ("id", "book_id", "title", "number", "order", "active", "create_at",
                  "origin_addr", "relate_chapter_id", "content", "book_title")

    def get_book_title(self, obj):
        book_obj = BookAdminModels.Book.normal.filter(id=obj.book_id).first()
        return book_obj.title

    def get_relate_chapter_id(self, obj):
        query_set = BookAdminModels.Chapter.normal.filter(
            book_id=obj.book_id).values("id")
        id_list = [item['id'] for item in query_set] if query_set else []
        index = id_list.index(obj.id)
        if index == 0:
            return {"pre_id": 0, "next_id": id_list[1]}
        elif index == len(id_list) - 1:
            return {"pre_id": id_list[index - 1], "next_id": 0}
        else:
            return {"pre_id": id_list[index - 1], "next_id": id_list[index + 1]}


class BookSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    cover = serializers.SerializerMethodField()

    class Meta:
        model = BookAdminModels.Book
        fields = ("id", "create_at", "status", "update_at", "title",
                  "collection_num", "click_num", "desc", "markup", "on_shelf",
                  "is_finished", "author", "latest_chapter", "cover", )
        read_only_fields = ("cover", )

    def get_cover(self, obj):
        return ComicAdminSerializers.CommonImageSerializer.to_representation(book_id=obj.id, img_type="book_cover", quality="title")


class BookDetailSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)
    # author = ComicAdminSerializers.AuthorSerializer()
    chapter = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = ComicAdminModels.Comic
        fields = ("id", "create_at", "status", "update_at", "title",
                  "collection_num", "click_num", "desc", "markup", "on_shelf",
                  "is_finished", "author", "latest_chapter", "chapter", "cover")

        read_only_fields = ("chapter", "cover")

    def get_chapter(self, obj):
        chapters = BookAdminModels.Chapter.normal.filter(book_id=obj.id)
        return ChapterSerializer(chapters, many=True).data

    def get_cover(self, obj):
        return ComicAdminSerializers.CommonImageSerializer.to_representation(book_id=obj.id, img_type="book_cover", quality="title", only_url=False)


class SpydersUtilsSerializer(serializers.Serializer):
    def to_representation(self):
        def run_subprocess(url):
            task_type = "start_book_spider_work"
            manage_path = os.path.join(settings.BASE_DIR, 'manage.py')
            subprocess.Popen(['python', manage_path, task_type, "-u", url])

        # run_subprocess("https://manhua.dmzj.com/zuixihuanderenwangjidaiyanjle/")
        run_subprocess("https://www.biqugex.com/book_31777/")
        # run_subprocess("https://www.biqudao.com/bqge91054/")
