from django.contrib.auth import \
    authenticate, \
    login as django_login, \
    logout as django_logout, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import LoginForm, SignupForm

User = get_user_model()


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


def profile(request, user_pk=None):
    # 0. urls.py와 연결
    #   urls.py참조
    #
    # 1. user_pk에 해당하는 User를 cur_user키로 render
    #   1.1. user = User.objects.filter(조건)
    #        context = {내용채우기}
    #        return render(인수 전달)
    # user = User.objects.get(pk=user_pk)
    # DoesNotExist Exception발생시 raise Http404

    """
    1. GET parameter로 'page'를 받아 처리
        page가 1일경우 Post의 author가 해당 User인
        Post목록을 -created_date순서로 page * 9만큼의
        QuerySet을 생성해서 리턴
        !!Pagination사용하지 말 것

        만약 실제 Post개수보다 큰 page가 왔을 경우, 최대한의 값을 보여줌
        'page'키의 값이 오지 않을 경우, int로 변환 불가능한 경우, 1보다 작은값일 경우 -> 1로 처리

    2. def follow_toggle(request, user_pk)
        위 함수기반 뷰를 구현
            login_required
            requirePOST
        데코레이터들을 사용(필요하다면 더 추가)
        처리 후 next값을 받아 처리하고,
            없을 경우 해당 User의 profile페이지로 이동

    **extra. 유저 차단기능 만들어보기
        Block여부는 Relation에서 다룸
            1. followers, following에 유저가 나타나면 안됨
            2. block_users로 차단한 유저 목록 QuerySet리턴
            3. follow, unfollow기능을 하기전에 block된 유저인지 확인
            4. block처리시 follow상태는 해제되어야 함 (동시적용 불가)
            4. 로그인 시 post_list에서 block_users의 글은 보이지 않도록 함
    """
    if user_pk:
        user = get_object_or_404(User, pk=user_pk)
    else:
        user = request.user
    context = {
        'cur_user': user,
    }
    return render(request, 'member/profile.html', context)

    # 2. member/profile.html작성, 해당 user정보 보여주기
    #   2-1. 해당 user의 followers, following목록 보여주기

    # 3. 현재 로그인한 유저가 해당 유저(cur_user)를 팔로우하고 있는지 여부 보여주기
    #   3-1. 팔로우하고 있다면 '팔로우 해제'버튼, 아니라면 '팔로우'버튼 띄워주기
    # 4~ -> def follow_toggle(request)뷰 생성
