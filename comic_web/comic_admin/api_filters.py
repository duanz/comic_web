from django_filters import rest_framework as filters
from comic_admin import models as ComicAdminModels


class ComicListFilter(filters.FilterSet):

    class Meta:
        model = ComicAdminModels.Comic
        fields = {
            'title': ['icontains'],
            'author': ['exact'],
        }