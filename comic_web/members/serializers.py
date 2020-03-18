from rest_framework import serializers
# from comic_admin import models as ComicAdminModels
# from book_admin import models as BookAdminModels
# from book_admin import serializers as BookAdminSerializers
# from django.conf import settings
# from comic_web.utils import photo as photo_lib
from members import models as MemberModels
from .tasks import handle_book_and_comic_spider_tasks

class TaskSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = MemberModels.Task
        fields = "__all__"
    
    def create(self, validated_data):
        handle_book_and_comic_spider_tasks.delay()
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        handle_book_and_comic_spider_tasks.delay()
        return super().update(instance, validated_data)


class ViewHistorySerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%I:%S", required=False)

    class Meta:
        model = MemberModels.MemberViewHistory
        fields = "__all__"
