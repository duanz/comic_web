from django_filters import rest_framework as filters
from book_admin import models as BookAdminModels


class BookListFilter(filters.FilterSet):

    class Meta:
        model = BookAdminModels.Book
        fields = {
            'title': ['icontains'],
            'author': ['exact'],
        }
