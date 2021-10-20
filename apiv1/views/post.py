from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from account.models import Profile
from post.models import PostModel, CommentModel
from ..serializers import (
    ProfileSerializer, CreateUpdateDeletePostSerializer, GetPostSerializer, CommentSerializer)
from ..permissions import IsOwnPostOrReadOnly


class CreateUpdateDeletePostView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = PostModel.objects.all()
    serializer_class = CreateUpdateDeletePostSerializer
    permission_classes = (IsOwnPostOrReadOnly, IsAuthenticated)

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class GetPostView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PostModel.objects.filter(is_public="public")
    serializer_class = GetPostSerializer
    # permission_classes = (IsOwnPostOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return PostModel.objects.filter(Q(is_public="public") | Q(posted_by=self.request.user))
        return PostModel.objects.filter(is_public="public")


@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
def post_user(request, id):
    if request.user.id == id:
        posts = get_user_model().objects.get(id=id).posted_by.all()
    else:
        posts = get_user_model().objects.get(id=id).posted_by.filter(is_public="public")
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# @api_view(['GET', 'POST'])
# @permission_classes((IsAuthenticated,))
# def get_followee_post(request):
#     posts = PostModel.objects.filter(posted_by__in=request.data["follow"])
#     paginator = PageNumberPagination()
#     paginator.page_size = 10
#     result_page = paginator.paginate_queryset(posts, request)
#     serializer = GetPostSerializer(result_page, many=True)
#     return paginator.get_paginated_response(serializer.data)


class GetFollowUserPost(generics.ListAPIView):
    serializer_class = GetPostSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # User = get_user_model().objects.get(id=self.request.user.id)
        following = Profile.objects.filter(followers=self.request.user)
        following_list = [str(i)
                          for i in following.values_list("user", flat=True)]
        return PostModel.objects.filter(posted_by__in=following_list)


@api_view(['GET'])
def post_search(request, id):
    try:
        posts = PostModel.objects.filter(Q(post__contains=id, is_public="public") | Q(
            post__contains=id, posted_by=request.user))
    except Exception as e:
        posts = PostModel.objects.filter(post__contains=id, is_public="public")
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@ api_view(['GET'])
def post_hashtag(request, id):
    try:
        posts = PostModel.objects.filter(
            Q(tags=id, is_public="public") | Q(tags=id, posted_by=request.user))
    except Exception as e:
        posts = PostModel.objects.filter(tag=id, is_public="public")
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
def like_post(request, id):
    # いいねをするもしくは外すUser
    user = request.user
    try:
        # いいねされるまたは外されるPost
        post_to_like = PostModel.objects.get(id=id)

        if user in post_to_like.liked.all():
            post_to_like.liked.remove(user)
            post_to_like.save()

            return Response({'result': 'unlike', 'post': post_to_like.id, 'unliked_by': user.id})
        else:
            post_to_like.liked.add(user)
            post_to_like.save()
            return Response({'result': 'like', 'post': post_to_like.id, 'liked_by': user.id})
    except Exception as e:
        message = {'detail': f'{e}'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
def get_profiles_like_post(request):
    liked_by = Profile.objects.filter(user_id__in=request.data["liked_by"])
    serializer = ProfileSerializer(liked_by, many=True)
    return Response(serializer.data)


@ api_view(['GET'])
@ permission_classes((IsAuthenticated,))
def get_favorite_post(request, id):
    posts = PostModel.objects.filter(liked=id)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@ api_view(['GET'])
@ permission_classes((IsAuthenticated,))
def comments(request, id):
    comments = CommentModel.objects.filter(post=id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = CommentModel.objects.all()
    serializer_class = CommentSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(commented_by=self.request.user)
