import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, TransactionTestCase

User = get_user_model()


class UserModelTest(TransactionTestCase):
    DUMMY_USERNAME = 'username'
    DUMMY_PASSWORD = 'password'

    @staticmethod
    def make_users(num):
        return [User.objects.create_user(username='username{}'.format(i)) for i in range(num)]

    def test_fields_default_value(self):
        """
        유저 생성시 필드의 기본값이 원하는 형태로 들어가 있는지
        """
        user = User.objects.create_user(
            username=self.DUMMY_USERNAME,
            password=self.DUMMY_PASSWORD
        )
        # first_name필드
        self.assertEqual(user.first_name, '')
        # last_name필드
        self.assertEqual(user.last_name, '')
        # email필드
        self.assertEqual(user.email, '')
        # user_type필드
        self.assertEqual(user.user_type, User.USER_TYPE_DJANGO)
        # nickname필드
        self.assertEqual(user.nickname, None)
        # img_profile필드
        self.assertEqual(user.img_profile, '')
        # relations
        self.assertEqual(user.relations.count(), 0)

    def test_follow(self):
        def follow_test_helper(source, following, non_following):
            for target in following:
                self.assertIn(target, source.following)
                self.assertIn(source, target.followers)
                self.assertTrue(source.is_follow(target))
                self.assertTrue(target.is_follower(source))
            for target in non_following:
                self.assertNotIn(target, source.following)
                self.assertNotIn(source, target.followers)
                self.assertFalse(source.is_follow(target))
                self.assertFalse(target.is_follower(source))

        # follow테스트를 위한 user 4명 생성
        # user1은 user2,3,4를 follow
        # user2는 user3,4를 follow
        # user3는 user4를 follow
        # user4는 아무도 follow하지 않음
        user1, user2, user3, user4 = self.make_users(4)
        user1.follow(user2)
        user1.follow(user3)
        user1.follow(user4)

        user2.follow(user3)
        user2.follow(user4)

        user3.follow(user4)

        follow_test_helper(
            source=user1,
            following=[user2, user3, user4],
            non_following=[]
        )
        follow_test_helper(
            source=user2,
            following=[user3, user4],
            non_following=[user1]
        )
        follow_test_helper(
            source=user3,
            following=[user4],
            non_following=[user1, user2],
        )
        follow_test_helper(
            source=user4,
            following=[],
            non_following=[user1, user2, user3],
        )

    def test_unfollow(self):
        """unfollow 메서드 테스트"""
        user1, user2 = self.make_users(2)
        user1.follow(user2)

        self.assertTrue(user1.is_follow(user2))
        self.assertTrue(user2.is_follower(user1))
        self.assertIn(user1, user2.followers)
        self.assertIn(user2, user1.following)

        user1.unfollow(user2)
        self.assertFalse(user1.is_follow(user2))
        self.assertFalse(user2.is_follower(user1))
        self.assertNotIn(user1, user2.followers)
        self.assertNotIn(user2, user1.following)

    def test_follow_toggle(self):
        user1, user2 = self.make_users(2)
        user1.follow_toggle(user2)

        self.assertTrue(user1.is_follow(user2))
        self.assertTrue(user2.is_follower(user1))
        self.assertIn(user1, user2.followers)
        self.assertIn(user2, user1.following)

        user1.follow_toggle(user2)
        self.assertFalse(user1.is_follow(user2))
        self.assertFalse(user2.is_follower(user1))
        self.assertNotIn(user1, user2.followers)
        self.assertNotIn(user2, user1.following)


class UserModelManagerTest(TransactionTestCase):
    def test_get_or_create_facebook_user(self):
        test_last_name = 'test_last_name'
        test_first_name = 'test_first_name'
        test_email = 'test_email@email.com'
        user_info = {
            'id': 'dummy_facebook_id',
            'last_name': test_last_name,
            'first_name': test_first_name,
            'email': test_email,
        }
        # 위의 user_info dict를 이용해 해당 내용을 테스트
        user = User.objects.get_or_create_facebook_user(user_info)

        # username테스트
        self.assertEqual(
            user.username,
            '{}_{}_{}'.format(
                User.USER_TYPE_FACEBOOK,
                settings.FACEBOOK_APP_ID,
                user_info['id']
            )
        )
        # usertype필드
        self.assertEqual(user.user_type, User.USER_TYPE_FACEBOOK)
        # lastname, first_name, email
        self.assertEqual(user.last_name, test_last_name)
        self.assertEqual(user.first_name, test_first_name)
        self.assertEqual(user.email, test_email)