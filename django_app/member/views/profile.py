from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from ..forms import UserEditForm

User = get_user_model()

__all__ = (
    'profile',
    'profile_edit',
)


def profile(request, user_pk=None):
    # 유저가 로그인하지 않았으며 user_pk도 주어지지 않은 경우 (my_profile에 접근하려는 경우)
    if not request.user.is_authenticated and not user_pk:
        # login view로 이동시키며 뒤의 next get parameter에 다시 profile view의 URL을 붙여줌
        login_url = reverse('member:login')
        redirect_url = login_url + '?next=' + request.get_full_path()
        return redirect(redirect_url)
    num_posts_per_page = 6
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
    """
    # GET parameter에 들어온 'page'값 처리
    page = request.GET.get('page', 1)
    try:
        page = int(page) if int(page) > 1 else 1
    except ValueError:
        page = 1
    except Exception as e:
        page = 1
        print(e)

    """
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

    # page * 9만큼의 Post QuerySet을 리턴. 정렬순서는 created_date 내림차순
    posts = user.post_set.order_by('-created_date')[:page * num_posts_per_page]
    post_count = user.post_set.count()
    # next_page = 현재 page에서 보여주는 Post개수보다 post_count가 클 경우 전달받은 page + 1, 아닐경우 None할당
    next_page = page + 1 if post_count > page * num_posts_per_page else None

    context = {
        'cur_user': user,
        'posts': posts,
        'post_count': post_count,
        'page': page,
        'next_page': next_page,
    }
    return render(request, 'member/profile.html', context)

    # 2. member/profile.html작성, 해당 user정보 보여주기
    #   2-1. 해당 user의 followers, following목록 보여주기

    # 3. 현재 로그인한 유저가 해당 유저(cur_user)를 팔로우하고 있는지 여부 보여주기
    #   3-1. 팔로우하고 있다면 '팔로우 해제'버튼, 아니라면 '팔로우'버튼 띄워주기
    # 4~ -> def follow_toggle(request)뷰 생성


@login_required
def profile_edit(request):
    """
    request.method == 'POST'일 때
        nickname과 img_profile(필드도 모델에 추가)을 수정할 수 있는
        UserEditForm을 구성 (ModelForm상속)
        및 사용

    1. UserEditForm구성
    2. 이 view에서 request method가 GET일때,
        해당 Form에 request.user에 해당하는 User를 이용해
        bound form을 만듬
    3. POST요청일 때, 받은 데이터를 이용해 Form에 bind된
        User instance를 업데이트
    """
    if request.method == 'POST':
        # UserEditForm에 수정할 data를 함께 binding
        form = UserEditForm(
            data=request.POST,
            files=request.FILES,
            instance=request.user
        )
        # data가 올바를 경우 (유효성 통과)
        if form.is_valid():
            # form.save()를 이용해 instance를 update
            form.save()
            return redirect('member:my_profile')
    else:
        form = UserEditForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'member/profile_edit.html', context)
