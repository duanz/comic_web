from rest_framework import serializers
# from comic_admin import models as ComicAdminModels
# from book_admin import models as BookAdminModels
# from book_admin import serializers as BookAdminSerializers
# from django.conf import settings
# from comic_web.utils import photo as photo_lib
from members import models as MemberModels


class TaskSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = MemberModels.Task
        fields = "__all__"


class ViewHistorySerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = MemberModels.MemberViewHistory
        fields = "__all__"
