from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from account.models import Profile
from post.models import PostModel, TagModel, CommentModel
from roadmap.models import RoadMapModel, StepModel, LookBackModel


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True, style={'input_type': 'password'})

    class Meta:
        # get_user_modelは現在有効なユーザーモデル（今回はカスタムしたUserモデル）を取得できる
        model = get_user_model()
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = get_user_model().objects.get(email=obj['email'])
        # print(obj)

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # if the given credentials are valid, return a User object.
        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid Credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        # 返り値は、serializer.validated_dataで確認できる？
        return {
            'email': user.email,
            # 'tokens': user.tokens()
        }


class ProfileSerializer(serializers.ModelSerializer):
    following = SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'nick_name', 'user',
                  'created_at', 'img', 'followers', 'following')
        extra_kwargs = {'user': {'read_only': True}}

    def get_following(self, obj):

        if obj.user is None:
            return None
        else:
            following = Profile.objects.filter(
                followers=obj.user).values()
            following_list = []
            for i in range(len(following)):
                following_list.append(following[i]['user_id'])
            return following_list


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = ['id', 'name']


class CreateUpdateDeletePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostModel
        fields = ['id', 'post', 'posted_by', 'liked', 'is_public', 'tags']
        extra_kwargs = {'posted_by': {'read_only': True}}

    def create(self, validated_data):
        tags = []
        # print(validated_data)
        # if validated_data.get('tags', None):
        #     validated_data.pop('tags')
        for word in validated_data['post'].split():
            if (word[0] == '#'):
                tag = TagModel.objects.filter(name=word[1:]).first()
                if tag:
                    tags.append(tag.pk)

                else:
                    tag = TagModel(name=word[1:])
                    tag.save()
                    tags.append(tag.pk)
        post = super().create(validated_data)
        post.tags.set(tags)
        return post


class GetPostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    nick_name = SerializerMethodField()
    img = SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:
        model = PostModel
        fields = ['id', 'post', 'posted_by', 'created_at', 'updated_at', 'liked',
                  'is_public', 'tags', 'nick_name', 'img']
        extra_kwargs = {'posted_by': {'read_only': True}}

    def get_nick_name(self, instance):
        if instance.posted_by is None:
            return None
        else:
            nick_name = Profile.objects.get(user=instance.posted_by).nick_name
            # print(type(nick_name), ':', nick_name)
            return str(nick_name)

    def get_img(self, instance):
        img = Profile.objects.get(user=instance.posted_by).img
        if img:
            # print(type(img), ':', img)
            return f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        return None


class CommentSerializer(serializers.ModelSerializer):
    commented_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    nick_name = SerializerMethodField()
    img = SerializerMethodField()

    class Meta:
        model = CommentModel
        fields = ['id', 'comment', 'commented_by',
                  'commented_at', 'post',  'nick_name', 'img']
        extra_kwargs = {'commented_by': {'read_only': True}}

    def get_nick_name(self, instance):
        if instance.commented_by is None:
            return None
        else:
            nick_name = Profile.objects.get(
                user=instance.commented_by).nick_name
            # print(type(nick_name), ':', nick_name)
            return str(nick_name)

    def get_img(self, instance):
        img = Profile.objects.get(user=instance.commented_by).img
        if img:
            # print(type(img), ':', img)
            return f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        return None


class RoadMapSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    # step = SerializerMethodField()
    nick_name = SerializerMethodField()
    img = SerializerMethodField()

    class Meta:
        model = RoadMapModel
        fields = ['id', 'title', 'overview', 'challenger',
                  'is_public', 'created_at', 'updated_at',
                  'nick_name', 'img']
        extra_kwargs = {'challenger': {'read_only': True}}

    def get_nick_name(self, instance):
        if instance.challenger is None:
            return None
        else:
            nick_name = Profile.objects.get(
                user=instance.challenger).nick_name
            # print(type(nick_name), ':', nick_name)
            return str(nick_name)

    def get_img(self, instance):
        img = Profile.objects.get(user=instance.challenger).img
        if img:
            # print(type(img), ':', img)
            return f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        return None
    # def get_step(self, instance):
    #     step = StepModel.objects.filter(
    #         roadmap=instance.id).order_by('step', 'created_at')
    #     if not step:
    #         return None
    #     return step


class StepSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    # roadmap = RoadMapSerializer(many=True)

    class Meta:
        model = StepModel
        fields = ['id', 'roadmap', 'to_learn', 'is_completed',
                  'order', 'created_at', 'updated_at']
        extra_kwargs = {'roadmap':  {'read_only': True},
                        'order':  {'read_only': True}}


class LookBackSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = LookBackModel
        fields = ['id', 'learned', 'step', 'created_at', 'updated_at']
        # extra_kwargs = {'step':  {'read_only': True}}
