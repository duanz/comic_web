from rest_framework import serializers
from comic_admin import models as ComicAdminModels


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


class ChapterImageSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = ComicAdminModels.ChapterImage
        fields = ('__all__')


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
    chapter = ChapterSerializer(many=True, read_only=True)
    # chapter = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ComicAdminModels.Comic
        fields = ("id", "create_at", "status", "update_at", "title", "collection_num",
                  "click_num", "desc", "markup", "on_shelf", "is_finished", "author", "chapter")
