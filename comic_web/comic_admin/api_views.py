from comic_admin import models as ComicAdminModels
from comic_admin import serializers as ComicAdminSerializers
from comic_admin import api_filters as ComicAdminFilters
from comic_web.utils.permission import IsAuthorization, BaseApiView, BaseGenericAPIView
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import mixins, filters
from django_filters import rest_framework


class IndexComicApiView(BaseApiView):
    """获取漫画首页"""
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return Response(data={"title": "这是测试"})


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