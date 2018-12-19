from django.urls import path
from members import api_views


app_name = "member"
urlpatterns = [
    # utils   --- 2018.11.23
    path(r'utils/task/', api_views.TaskApiView.as_view()),
    path(r'utils/task/<int:pk>/', api_views.TaskDetailApiView.as_view()),

    # history   --- 2018.11.23
    path(r'history/', api_views.ViewHistoryApiView.as_view()),
]
