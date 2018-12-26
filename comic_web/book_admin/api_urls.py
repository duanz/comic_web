from django.urls import path
from book_admin import api_views


app_name = "book_admin"
urlpatterns = [
    path(r'book/index/', api_views.BookIndexApiView.as_view()),
    path(r'book/', api_views.BookListApiView.as_view()),
    path(r'book/<int:pk>/', api_views.BookDetailApiView.as_view()),

    path(r'book/chapter/list/<int:pk>/', api_views.BookChanpterListApiView.as_view()),
    path(r'book/chapter/<int:pk>/', api_views.BookChapterDetailApiView.as_view()),


    # utils   --- 2018.11.23
    path(r'book/utils', api_views.SpyderUtilsApiView.as_view()),
]
