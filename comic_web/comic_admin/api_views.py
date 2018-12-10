from comic_admin import models as ComicAdminModels
from comic_admin import serializers as ComicAdminSerializers
from comic_admin import api_filters as ComicAdminFilters
from comic_web.utils.permission import IsAuthorization, BaseApiView, BaseGenericAPIView
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import mixins, filters
from django_filters import rest_framework


class ComicIndexApiView(BaseApiView):
    """获取漫画首页"""
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        data = ComicAdminSerializers.DefaultIndexSerializer().to_representation("comic")
        return Response(data)


class ComicCoverImageApiView(mixins.ListModelMixin, mixins.CreateModelMixin, BaseGenericAPIView):
    """
    get: 反馈信息详情；
    """
    queryset = ComicAdminModels.CoverImage.normal.filter(active=True)
    serializer_class = ComicAdminSerializers.CoverImageSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ComicListApiView(mixins.ListModelMixin, BaseGenericAPIView):
    """获取漫画列表"""

    queryset = ComicAdminModels.Comic.normal.filter(on_shelf=True)
    serializer_class = ComicAdminSerializers.ComicSerializer

    filter_backends = (rest_framework.DjangoFilterBackend, )
    filter_class = ComicAdminFilters.ComicListFilter

    ordering_fields = (
        'title',
        'author',
    )

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ComicDetailApiView(mixins.RetrieveModelMixin, BaseGenericAPIView):
    """
    get: 反馈信息详情；
    """
    queryset = ComicAdminModels.Comic.normal.filter(on_shelf=True)
    serializer_class = ComicAdminSerializers.ComicDetailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ComicChapterDetailApiView(mixins.RetrieveModelMixin, BaseGenericAPIView):
    """
    get: 反馈信息详情；
    """
    queryset = ComicAdminModels.Chapter.normal.filter(active=True)
    serializer_class = ComicAdminSerializers.ChapterDetailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SpyderUtilsApiView(BaseApiView):
    "get: 下发爬虫任务"
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        ComicAdminSerializers.SpydersUtilsSerializer().to_representation()
        return Response("success")


class HistoryApiView(BaseApiView):
    "get: 获取浏览历史"
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        data = [
            {'id': 1, 'data_type': 'book', 'title': '我不成仙',
                'chapter_id': 50, 'content_id': 1, 'chapter_title': '第50章 要上天吗'},
            {'id': 2, 'data_type': 'book', 'title': '我不成仙',
                'chapter_id': 51, 'content_id': 1, 'chapter_title': '第60章 要上天'},
            {'id': 3, 'data_type': 'comic', 'title': '这是漫画',
                'chapter_id': 1, 'content_id': 2, 'chapter_title': '第1章 测ui'},
        ]
        return Response(data)
