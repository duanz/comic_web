from django.contrib.auth import authenticate, login, logout
from django_filters import rest_framework
from rest_framework import filters, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from comic_web.utils.permission import IsAuthorization, BaseApiView, BaseGenericAPIView
from members import api_filters as MemberFilters
from members import models as MemberModels
from members import serializers as MemberSerializers


class MemberCreate(mixins.CreateModelMixin, BaseGenericAPIView):
    '''
    post: 添加用户.
    '''

    queryset = MemberModels.Member.objects.all()
    serializer_class = MemberSerializers.MemberSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MemberDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, BaseGenericAPIView):
    '''
    get: 获取用户信息；
    put: 更新用户；
    delete: 删除用户。
    '''

    queryset = MemberModels.Member.normal.all()
    serializer_class = MemberSerializers.MemberSerializer
    permission_classes = (IsAuthorization, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        kwargs.update({'partial': True})
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_object(self):
        return MemberModels.Member.normal.filter(pk=self.request.user.id).first()


class MemberLoginApiView(BaseApiView):
    '''post: 使用用户名密码登录'''

    queryset = MemberModels.Member.normal.all()
    serializer_class = MemberSerializers.MemberLoginSerializer
    permission_classes = (AllowAny,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, format=None):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active and user.status not in ['deleted', 'delete']:
            user.ip_address = request.META.get('REMOTE_ADDR')
            user.save()
            login(request, user)
            serializer = MemberSerializers.MemberSerializer(user, context={'request': request})
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({'msg': '用户名或密码错误', 'code': HTTP_400_BAD_REQUEST, 'result': 'FAIL'}, status=HTTP_200_OK)

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        """
        pass


class MemberLogoutApiView(BaseApiView):
    '''post: 注销登录'''

    queryset = MemberModels.Member.normal.all()
    serializer_class = MemberSerializers.MemberSerializer
    permission_classes = (IsAuthorization,)

    def post(self, request, format=None):
        logout(request)
        return Response({'msg': '退出成功', 'code': HTTP_200_OK, 'result': 'SUCCESS'}, status=HTTP_200_OK)


class TaskApiView(mixins.ListModelMixin, mixins.CreateModelMixin, BaseGenericAPIView):
    """
    get: 获取任务列表
    post: 添加任务
    """
    queryset = MemberModels.Task.normal.filter()
    serializer_class = MemberSerializers.TaskSerializer
    permission_classes = (IsAuthorization, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in self.permission_classes]
        else:
            return [IsAuthorization()]


class TaskDetailApiView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, BaseGenericAPIView):
    """
    get: 获取任务详情
    post: 修改任务
    delete: 删除任务
    """
    queryset = MemberModels.Task.normal.filter()
    serializer_class = MemberSerializers.TaskSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):        
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in self.permission_classes]
        else:
            return [IsAuthorization()]


class ViewHistoryApiView(mixins.ListModelMixin, mixins.CreateModelMixin, BaseGenericAPIView):
    """
    get: 获取浏览历史；
    post: 提交本地浏览记录
    """
    queryset = MemberModels.MemberViewHistory.normal.filter()
    serializer_class = MemberSerializers.ViewHistorySerializer
    permission_classes = (IsAuthorization, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)