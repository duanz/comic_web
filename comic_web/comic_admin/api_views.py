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
    get: 获取漫画封面；
    post: 创建漫画封面；
    """
    queryset = ComicAdminModels.CoverImage.normal.filter(active=True)
    serializer_class = ComicAdminSerializers.CoverImageSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in self.permission_classes]
        else:
            return [IsAuthorization()]


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


class ComicDetailApiView(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, BaseGenericAPIView):
    """
    get: 获取漫画详情；
    delete: 删除漫画;
    """
    queryset = ComicAdminModels.Comic.normal.filter(on_shelf=True)
    serializer_class = ComicAdminSerializers.ComicDetailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
     
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in self.permission_classes]
        else:
            return [IsAuthorization()]


class ComicChapterDetailApiView(mixins.RetrieveModelMixin, BaseGenericAPIView):
    """
    get: 获取漫画章节详情；
    """
    queryset = ComicAdminModels.Chapter.normal.filter(active=True)
    serializer_class = ComicAdminSerializers.ChapterDetailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class IndexBlockApiView(mixins.CreateModelMixin, mixins.ListModelMixin, BaseGenericAPIView):
    """
    get: 获取首页块；
    post: 创建首页块；
    """
    queryset = ComicAdminModels.IndexBlock.normal.all()
    serializer_class = ComicAdminSerializers.IndexBlockSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in self.permission_classes]
        else:
            return [IsAuthorization()]


class IndexBlockDetailApiView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, BaseGenericAPIView):
    """
    get: 获取首页块详情；
    post: 更新首页块详情；
    """
    queryset = ComicAdminModels.IndexBlock.normal.all()
    serializer_class = ComicAdminSerializers.IndexBlockSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in self.permission_classes]
        else:
            return [IsAuthorization()]

