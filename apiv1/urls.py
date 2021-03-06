from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import account, post, roadmap

app_name = 'apiv1'

router = DefaultRouter()
router.register('profile', account.ProfileViewSet)
router.register('post', post.GetPostView)
router.register('create_update_delete_post', post.CreateUpdateDeletePostView)
router.register('comment', post.CommentViewSet)
router.register('roadmap', roadmap.RoadMapViewSet)
router.register('step', roadmap.StepViewSet)
router.register('lookback', roadmap.LookBackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # register, login
    path('register/', account.RegisterView.as_view(), name="register"),
    path('delete-account/<uuid:pk>/',
         account.DeleteUserView.as_view(), name="delete"),
    path('email-verify/', account.VerifyEmail.as_view(), name="email-verify"),
    path('login/', account.LoginApiView.as_view(), name="login"),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    # profile
    path('myprofile/', account.MyProfileListView.as_view(), name='myprofile'),
    path('<uuid:id>/following/',
         account.get_following, name='get-following-profile'),
    path('followers/', account.get_followers, name='get-followers-profile'),
    path('follow/<uuid:id>/', account.follow_user, name="follow-user"),
    # post
    path('post/user/<uuid:id>/', post.post_user, name='post-user'),
    path('followuser/post/', post.GetFollowUserPost.as_view(), name='post-follow'),
    path('post/favorite/<uuid:id>/', post.get_favorite_post, name="favorite-post"),
    path('post/like/<uuid:id>/', post.like_post, name="like-post"),
    path('post/like/profile/', post.get_profiles_like_post,
         name='get-profiles-like-post'),
    path('post/search/<str:id>/', post.post_search, name="search-post"),
    path('post/hashtag/<uuid:id>/', post.post_hashtag, name="post-hashtag"),
    path('post/<uuid:id>/comment/', post.comments, name="post-comments"),
    # roadmap
    path('roadmap/user/<uuid:id>/', roadmap.roadmap_user, name='roadmap-user'),
    path('followuser/roadmap/', roadmap.GetFollowUserRoadmap.as_view(),
         name="roadmap-follow"),
    path('roadmap/search/<str:id>/', roadmap.roadmap_search, name="search-roadmap"),
    path('step/roadmap/<uuid:id>/', roadmap.steps, name='step-roadmap'),
    path('step/change-order', roadmap.change_step_order, name='change-step-order'),
    path('lookback/step/<uuid:id>/', roadmap.lookbacks, name='lookback-step')
]
