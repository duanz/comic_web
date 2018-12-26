from book_admin import models as BookAdminModels
from book_admin import serializers as BookAdminSerializers
from book_admin import api_filters as BookAdminFilters
from comic_admin import serializers as ComicAdminSerializers
from comic_web.utils.permission import IsAuthorization, BaseApiView, BaseGenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import mixins
from django_filters import rest_framework


class BookIndexApiView(BaseApiView):
    """获取小说首页"""
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        data = ComicAdminSerializers.DefaultIndexSerializer().to_representation("book")
        return Response(data)


class BookListApiView(mixins.ListModelMixin, BaseGenericAPIView):
    """获取小说列表"""

    queryset = BookAdminModels.Book.normal.filter(on_shelf=True)
    serializer_class = BookAdminSerializers.BookSerializer

    filter_backends = (rest_framework.DjangoFilterBackend, )
    filter_class = BookAdminFilters.BookListFilter

    ordering_fields = (
        'title',
        'author',
    )

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BookDetailApiView(mixins.RetrieveModelMixin, BaseGenericAPIView):
    """
    get: 反馈信息详情；
    """
    queryset = BookAdminModels.Book.normal.filter(on_shelf=True)
    serializer_class = BookAdminSerializers.BookDetailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class BookChapterDetailApiView(mixins.RetrieveModelMixin, BaseGenericAPIView):
    """
    get: 反馈信息详情；BookChanpterListApiView
    """
    queryset = BookAdminModels.Chapter.normal.filter(active=True)
    serializer_class = BookAdminSerializers.ChapterDetailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class BookChanpterListApiView(mixins.ListModelMixin, BaseGenericAPIView):
    """
    get: 获取小说章节列表；
    """
    queryset = BookAdminModels.Chapter.normal.filter(active=True)
    serializer_class = BookAdminSerializers.ChapterSerializer

    filter_backends = (rest_framework.DjangoFilterBackend, )
    filter_class = BookAdminFilters.ChapterListFilter

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(book_id=self.kwargs['pk'])


class SpyderUtilsApiView(BaseApiView):
    "get: 下发小说爬虫任务"
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        BookAdminSerializers.SpydersUtilsSerializer().to_representation()
        return Response("success")
