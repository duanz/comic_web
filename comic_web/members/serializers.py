from rest_framework import serializers
from rest_framework.authtoken.models import Token
from members import models as MemberModels
from .tasks import handle_book_and_comic_spider_tasks
import logging


class MemberSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = MemberModels.Member
        fields = ('id', 'username', 'gender', 'is_staff',
                  'password', 'email', 'token', 'avatar_url')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'token': {'read_only': True},
        }

    def create(self, validated_data):
        user = MemberModels.Member()
        user.username = validated_data.get('username', '')
        user.set_password(validated_data.get('password'))
        user.gender = validated_data.get('gender')
        user.email = validated_data.get('email')
        user.ip_address = validated_data.get('ip_address', '')
        user.avatar_url = validated_data.get('avatar_url', '')
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.get('password'))
            validated_data.pop('password')
        return super().update(instance, validated_data)

    def get_token(self, obj):
        try:
            if self.context.get('request').user.id != obj.id:
                logging.info(
                    'get token illegal, data not belong to current user')
                return ''
            token = Token.objects.get_or_create(user=obj)[0].key
            return token
        except Exception as e:
            logging.error('get token error: {}'.format(e))
            return ''

    def validate_username(self, value):
        method = self.context.get('request').method
        try:
            member = MemberModels.Member.normal.get(username__exact=value)
        except MemberModels.Member.DoesNotExist:
            member = False

        if member and method in ['POST', 'PUT']:
            raise serializers.ValidationError('该名称已存在.')
        return value
    

class MemberLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberModels.Member
        fields = ('username', 'password')


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
