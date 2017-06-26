from pprint import pprint

import re
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import \
    login as django_login, \
    logout as django_logout, get_user_model
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import redirect, render

from ..forms import LoginForm, SignupForm

User = get_user_model()

__all__ = (
    'login',
    'logout',
    'signup',
    'facebook_login',
)


def login(request):
    # member/login.html 생성
    #   username, password, button이 있는 HTML생성
    #   POST요청이 올 경우 좌측 코드를 기반으로 로그인 완료 후 post_list로 이동
    #   실패할경우 HttpResponse로 'Login invalid!'띄워주기

    # member/urls.py생성
    #   /member/login/으로 접근시 이 view로 오도록 설정
    #   config/urls.py에 member/urls.py를 include
    #       member/urls.py에 app_name설정으로 namespace지정

    # POST요청이 왔을 경우
    if request.method == 'POST':
        ### Form클래스 미사용시
        # 요청받은 POST데이터에서 username, password키가 가진 값들을
        # username, password변수에 할당 (문자열)
        # username = request.POST['username']
        # password = request.POST['password']

        # authenticate함수를 사용해서 User객체를 얻어 user에 할당
        # 인증에 실패할 경우 user변수에는 None이 할당됨
        # user = authenticate(
        #     request,
        #     username=username,
        #     password=password
        # )
        # user변수가 None이 아닐 경우 (정상적으로 인증되어 User객체를 얻은 경우)
        # if user is not None:
        #     # Django의 session을 이용해 이번 request와 user객체를 사용해 로그인 처리
        #     # 이후의 request/response에서는 사용자가 인증된 상태로 통신이 이루어진다
        #     django_login(request, user)
        #     # 로그인 완료후에는 post_list뷰로 리다이렉트 처리
        #     return redirect('post:post_list')

        ### Form클래스 사용시
        #   Bound form생성
        form = LoginForm(data=request.POST)
        # Bound form의 유효성을 검증
        #   https://docs.djangoproject.com/en/1.11/topics/forms/#building-a-form-in-django
        if form.is_valid():
            user = form.cleaned_data['user']
            django_login(request, user)
            # 일반적인 경우에는 post_list로 이동하지만,
            # GET parameter의 next속성값이 있을 경우 해당 URL로 이동
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect('post:post_list')
    # GET요청이 왔을 경우 (단순 로그인 Form보여주기)
    else:
        # 만약 이미 로그인 된 상태일 경우에는
        # post_list로 redirect
        # 아닐경우 login.html을 render해서 리턴
        if request.user.is_authenticated:
            return redirect('post:post_list')
        # LoginForm인스턴스를 생성해서 context에 넘김
        form = LoginForm()
    context = {
        'form': form,
    }
    # render시 context에는 LoginForm클래스형 form객체가 포함됨
    return render(request, 'member/login.html', context)


def logout(request):
    # 로그아웃되면 post_list로 redirect
    django_logout(request)
    return redirect('post:post_list')


def signup(request):
    # url은 /member/signup/$
    # member/signup.html을 사용
    #   username, password1, password2를 받아 회원가입
    #   이미 유저가 존재하는지 검사
    #   password1, 2가 일치하는지 검사
    #   각각의 경우를 검사해서 틀릴경우 오류메시지 리턴
    #   가입에 성공시 로그인시키고 post_list로 리다이렉트
    if request.method == 'POST':
        ### Form을 사용하지 않는 경우
        # username, password1, password2에 POST로 전달받은 데이터를 할당
        # username = request.POST['username']
        # password1 = request.POST['password1']
        # password2 = request.POST['password2']
        # # username에 해당하는 User가 있는지 검사
        # if User.objects.filter(username=username).exists():
        #     # 이미 존재하는 username일경우
        #     return HttpResponse('Username is already exist')
        # # password1과 password2가 같은지 검사
        # elif password1 != password2:
        #     # 다를경우
        #     return HttpResponse('Password and Password check are not equal')
        # # 위의 두 경우가 아닌 경우 유저를 생성
        # user = User.objects.create_user(
        #     username=username,
        #     password=password1
        # )

        ### Form을 사용한 경우
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.create_user()
            django_login(request, user)
            return redirect('post:post_list')
    else:
        form = SignupForm()
    context = {
        'form': form,
    }
    return render(request, 'member/signup.html', context)


def facebook_login(request):
    # facebook_login view가 처음 호출될 때
    #   유저가 Facebook login dialog에서 로그인 후, 페이스북에서 우리서비스 (Consumer)쪽으로
    #   GET parameter를 이용해 'code'값을 전달해줌 (전달받는 주소는 위의 uri_redirect)
    code = request.GET.get('code')
    app_access_token = '{}|{}'.format(
        settings.FACEBOOK_APP_ID,
        settings.FACEBOOK_SECRET_CODE,
    )

    # Exception을 상속받아 CustomException을 생성
    class GetAccessTokenException(Exception):
        def __init__(self, *args, **kwargs):
            error_dict = args[0]['data']['error']
            self.code = error_dict['code']
            self.message = error_dict['message']
            self.is_valid = error_dict['is_valid']
            self.scopes = error_dict['scopes']

    class DebugTokenException(Exception):
        def __init__(self, *args, **kwargs):
            error_dict = args[0]['data']['error']
            self.code = error_dict['code']
            self.message = error_dict['message']

    def add_message_and_redirect_referer():
        """
        페이스북 로그인 오류 메시지를 request에 추가하고, 이전 페이지로 redirect
        :return: redirect
        """
        # 유저용 메세지
        error_message_for_user = 'Facebook login error'
        # request에 에러메세지를 전달
        messages.error(request, error_message_for_user)
        # 이전페이지로 redirect
        return redirect(request.META['HTTP_REFERER'])

    def get_access_token(code):
        """
        code를 받아 액세스토큰 교환 URL에 요청, 이후 해당 액세스토큰을 반환
        오류 발생시 오류메시지를 리턴
        :param code:
        :return:
        """
        # 액세스토큰의 코드를 교환할 URL
        url_access_token = 'https://graph.facebook.com/v2.9/oauth/access_token'

        # 이전에 요청했던 redirect_uri와 같은 값을 만들어 줌 (access_token을 요청할 때 필요함)
        redirect_uri = '{}://{}{}'.format(
            request.scheme,
            request.META['HTTP_HOST'],
            request.path,
        )
        # 액세스토큰의 코드 교환
        # uri생성을 위한 params
        url_access_token_params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': redirect_uri,
            'client_secret': settings.FACEBOOK_SECRET_CODE,
            'code': code,
        }
        # 해당 URL에 get요청 후 결과 (json형식)를 파이썬 object로 변환 (result변수)
        response = requests.get(url_access_token, params=url_access_token_params)
        result = response.json()
        if 'access_token' in result:
            return result['access_token']
        # 액세스토큰 코드교환 결과에 오류가 있을 경우
        # 해당 오류를 request에 message로 넘기고 이전페이지 (HTTP_REFERER)로 redirect
        elif 'error' in result:
            raise GetAccessTokenException(result)
        else:
            raise Exception('Unknown error')

    def debug_token(token):
        url_debug_token = 'https://graph.facebook.com/debug_token'
        url_debug_token_params = {
            'input_token': token,
            'access_token': app_access_token
        }
        response = requests.get(url_debug_token, url_debug_token_params)
        result = response.json()
        if 'error' in result['data']:
            raise DebugTokenException(result)
        else:
            return result

    def get_user_info(user_id, token):
        url_user_info = 'https://graph.facebook.com/v2.9/{user_id}'.format(user_id=user_id)
        url_user_info_params = {
            'access_token': token,
            'fields': ','.join([
                'id',
                'name',
                'email',
                'first_name',
                'last_name',
                'picture.type(large)',
                'gender',
            ])
        }
        response = requests.get(url_user_info, params=url_user_info_params)
        result = response.json()
        return result

    # code키값이 존재하지 않으면 로그인을 더이상 진행하지 않음
    if not code:
        return add_message_and_redirect_referer()
    try:
        # 이 view에 GET parameter로 전달된 code를 사용해서 access_token을 받아옴
        # 성공시 access_token값을 가져옴
        # 실패시 GetAccessTokenException이 발생
        access_token = get_access_token(code)

        # 위에서 받아온 access_token을 이용해 debug_token을 요청
        # 성공시 토큰을 디버그한 결과 (user_id, scopes 등..)이 리턴
        # 실패시 DebugTokenException이 발생
        debug_result = debug_token(access_token)

        # debug_result에 있는 user_id값을 이용해서 GraphAPI에 유저정보를 요청
        user_info = get_user_info(user_id=debug_result['data']['user_id'], token=access_token)
        user = User.objects.get_or_create_facebook_user(user_info)

        # 해당 request에 유저를 로그인시킴
        django_login(request, user)
        return redirect(request.META['HTTP_REFERER'])

    except GetAccessTokenException as e:
        print(e.code)
        print(e.message)
        return add_message_and_redirect_referer()
    except DebugTokenException as e:
        print(e.code)
        print(e.message)
        return add_message_and_redirect_referer()
