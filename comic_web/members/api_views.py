from members import models as MemberModels
from members import serializers as MemberSerializers
from members import api_filters as MemberFilters
from comic_web.utils.permission import IsAuthorization, BaseApiView, BaseGenericAPIView
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import mixins, filters
from django_filters import rest_framework


class TaskApiView(mixins.ListModelMixin, mixins.CreateModelMixin, BaseGenericAPIView):
    """
    get: 获取任务列表
    post: 添加任务
    """
    queryset = MemberModels.Task.normal.filter()
    serializer_class = MemberSerializers.TaskSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TaskDetailApiView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, BaseGenericAPIView):
    """
    get: 获取任务详情
    post: 修改任务
    """
    queryset = MemberModels.Task.normal.filter()
    serializer_class = MemberSerializers.TaskSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ViewHistoryApiView(mixins.ListModelMixin, mixins.CreateModelMixin, BaseGenericAPIView):
    """
    get: 反馈信息详情；
    """
    queryset = MemberModels.MemberViewHistory.normal.filter()
    serializer_class = MemberSerializers.ViewHistorySerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
