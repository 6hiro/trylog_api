from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect
import jwt
from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from account.models import Profile
from ..serializers import UserSerializer, LoginSerializer, ProfileSerializer
from ..permissions import InOwnOrReadOnly, IsOwnProfileOrReadOnly
from ..utils import Util


class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data

            user = get_user_model().objects.get(email=user_data['email'])
            token = RefreshToken.for_user(user).access_token

            current_site = get_current_site(request).domain
            relativeLink = reverse('apiv1:email-verify')

            absrul = 'http://' + current_site + \
                relativeLink + "?token=" + str(token)
            email_body = user.email + \
                'さん、ご登録ありがとうございます。\nメールアドレスに間違いがなければ、以下のリンクからログインしてください。 \n' + absrul
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'メールアドレスを確認してください'}
            Util.send_email(data)

            return Response(user_data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    def get(self, request):

        token = request.query_params.get('token')
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')
            user = get_user_model().objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                Profile.objects.create(user=user, nick_name='ななしさん')

            # return Response({'email': 'Succressfully activated'}, status=status.HTTP_200_OK)
            redirect_url = 'http://localhost:3000'
            return redirect(redirect_url)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Acctivation Expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid()
        # res = Response(
        #     {"email": serializer.data["email"]}, status=status.HTTP_200_OK)
        # res.set_cookie(
        #     serializer.data["tokens"]["access"],
        #     max_age=60*20,
        #     httponly=True
        # )
        # res.set_cookie(
        #     serializer.data["tokens"]["refresh"],
        #     max_age=60*60*12,
        #     httponly=True
        # )
        return Response(serializers.data, status=status.HTTP_200_OK)


class DeleteUserView(generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (InOwnOrReadOnly,)


@ api_view(['GET'])
@ permission_classes((IsAuthenticated,))
def get_following(request, id):
    following = Profile.objects.filter(followers=id)
    serializers = ProfileSerializer(following, many=True)
    return Response(serializers.data)


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
def get_followers(request):
    followers = Profile.objects.filter(user_id__in=request.data["followers"])
    serializers = ProfileSerializer(followers, many=True)
    return Response(serializers.data)


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
def follow_user(request, id):
    # followする側のUser
    user = request.user
    try:
        # followされる側のUser
        user_to_follow = get_user_model().objects.get(id=id)
        # followされる側のUserのプロフィール（one to one の逆参照）
        user_to_follow_profile = user_to_follow.profile

        if user == user_to_follow:
            return Response({'result': 'You can not follow yourself'})

        if user in user_to_follow_profile.followers.all():
            user_to_follow_profile.followers.remove(user)
            user_to_follow_profile.save()
            return Response({'result': 'unfollow', 'unfollower': user.id, 'unfollowing': user_to_follow.id})
        else:
            user_to_follow_profile.followers.add(user)
            user_to_follow_profile.save()
            return Response({'result': 'follow', 'follower': user.id, 'following': user_to_follow.id})
    except Exception as e:
        message = {'detail': f'{e}'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnProfileOrReadOnly,)
    lookup_field = 'user'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
