from django_filters import rest_framework as filters
from book_admin import models as BookAdminModels


class BookListFilter(filters.FilterSet):

    class Meta:
        model = BookAdminModels.Book
        fields = {
            'title': ['icontains'],
            'author': ['exact'],
        }


class ChapterListFilter(filters.FilterSet):

    class Meta:
        model = BookAdminModels.Chapter
        fields = {
            'active': ['exact'],
            'number': ['exact'],
            'title': ['icontains'],
            'origin_addr': ['icontains'],
        }
