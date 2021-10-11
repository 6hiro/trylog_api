from django.test import TestCase
from django.utils.timezone import localtime
from django.contrib.auth import get_user_model
from account.models import Profile
from post.models import PostModel, TagModel
from ..serializers import UserSerializer, CreateUpdateDeletePostSerializer, GetPostSerializer, TagSerializer, CommentSerializer


class TestUserSerializer(TestCase):
    def test_input_valid(self):
        input_data = {
            "email": "demo@demo.demo",
            "password": "registration"
        }
        serializer = UserSerializer(data=input_data)
        self.assertEqual(serializer.is_valid(), True)

    def test_input_invalid_if_email_is_blank(self):
        input_data = {
            "email": "",
            "password": "registration"
        }
        serializer = UserSerializer(data=input_data)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['email'])
        self.assertCountEqual(
            [str(x) for x in serializer.errors['email']],
            ['この項目は空にできません。'],
        )

    def test_output_data(self):
        user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )
        serializer = UserSerializer(instance=user)
        self.assertEqual(serializer.data['email'], user.email)


class TestCreateUpdateDeletePostSerializer(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )

    def test_input_valid(self):
        input_data = {
            'post': 'test #test',
            'is_public': 'public',
        }
        serializer = CreateUpdateDeletePostSerializer(data=input_data)
        self.assertEqual(serializer.is_valid(), True)
        # print(serializer.validated_data)

    def test_input_invalid_if_post_is_blank(self):
        input_data = {
            'post': '',
            'is_public': 'public',
            'posted_by': self.user
        }
        serializer = CreateUpdateDeletePostSerializer(data=input_data)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['post'])
        # print([str(x) for x in serializer.errors['post']][0])
        self.assertCountEqual(
            [str(x) for x in serializer.errors['post']],
            ['この項目は空にできません。'],
        )

    def test_output_data(self):
        # Profile.objects.create(
        #     user=self.user,
        #     nick_name='nanashi'
        # )

        post = PostModel.objects.create(
            post='test #test',
            is_public='public',
            posted_by=self.user
        )
        serializer = CreateUpdateDeletePostSerializer(instance=post)
        # print(serializer.is_valid)

        # expected_data = {
        #     'id': str(post.id),
        #     'post': post.post,
        #     'posted_by': post.posted_by,
        #     'is_public': post.is_public,
        #     'tags': post.tags,
        #     'created_at': str(localtime(post.created_at)).replace('', 'T'),
        #     'updated_at': str(localtime(post.updated_at)).replace('', 'T')
        # }
        # self.assertDictEqual(serializer.data, expected_data)
        # print(serializer.data)
        self.assertEqual(serializer.data['id'], str(post.id))
        self.assertEqual(serializer.data['post'], post.post)
        self.assertEqual(serializer.data['is_public'], post.is_public)
