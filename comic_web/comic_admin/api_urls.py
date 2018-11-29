from django.urls import path
from comic_admin import api_views


app_name = "comic_admin"
urlpatterns = [
    path(r'comic/index/', api_views.ComicIndexApiView.as_view()),
    path(r'comic/', api_views.ComicListApiView.as_view()),
    path(r'comic/<int:pk>/', api_views.ComicDetailApiView.as_view()),

    path(r'comic/cover/', api_views.ComicCoverImageApiView.as_view()),

    path(r'comic/chapter/<int:pk>/', api_views.ComicChapterDetailApiView.as_view()),


    # utils   --- 2018.11.23
    path(r'utils', api_views.SpyderUtilsApiView.as_view()),
]
