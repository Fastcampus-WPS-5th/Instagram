from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By

User = get_user_model()


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.quit()

    def test_root_url_redirect_to_post_list_view(self):
        # live_server_url (root url)로 접근 시
        self.browser.get(self.live_server_url)

        # post_list view의 URL을 reverse()로 가져옴 ('/post/'일 것임)
        # post_list_url = reverse('post:post_list')
        # 사용자 입장이기 때문에 리터럴 문자열을 사용
        post_list_url = '/post/'

        # browser의 current_url이 live_server_url + '/post/'와 같은지 검사
        self.assertEqual(
            self.live_server_url + post_list_url,
            self.browser.current_url
        )

    def test_not_authenticated_user_redirect_to_login_view(self):
        urls = [
            '/member/profile/',
            '/member/profile/edit/',
            '/post/create/',
        ]
        for url in urls:
            self.browser.get(self.live_server_url + url)
            self.assertIn(
                self.live_server_url + '/member/login/',
                self.browser.current_url,
            )

    def test_not_authenticated_user_can_view_login_form(self):
        # 로그인하지 않은 유저가 화면에서 로그인 폼을 볼 수 있는지 테스트
        self.browser.get(self.live_server_url)
        form_login = self.browser.find_element_by_class_name('form-inline-login')
        input_username = form_login.find_element_by_id('id_username')
        input_password = form_login.find_element_by_id('id_password')
        button_submit = form_login.find_element_by_tag_name('button')

    def test_not_authenticated_user_can_login(self):
        test_username = 'username'
        test_password = 'password'
        User.objects.create_user(
            username=test_username,
            password=test_password
        )
        # 로그인하지 않은 유저가 화면의 로그인 폼을 이용해서 로그인 할 수 있는지 테스트
        self.browser.get(self.live_server_url)
        form_login = self.browser.find_element_by_class_name('form-inline-login')
        input_username = form_login.find_element_by_id('id_username')
        input_password = form_login.find_element_by_id('id_password')
        button_submit = form_login.find_element_by_tag_name('button')

        # 폼에 값을 입력하고 로그인 버튼 클릭
        input_username.send_keys(test_username)
        input_password.send_keys(test_password)
        button_submit.click()

        # 화면에 로그인 한 유저의 유저명이 표시되는지 확인
        top_header = self.browser.find_element_by_class_name('top-header')
        self.assertIn(
            test_username,
            top_header.text
        )
