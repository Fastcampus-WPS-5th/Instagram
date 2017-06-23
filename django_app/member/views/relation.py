from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

User = get_user_model()

__all__ = (
    'follow_toggle',
)


@require_POST
@login_required
def follow_toggle(request, user_pk):
    # 'next' GET parameter값을 가져옴
    next = request.GET.get('next')
    # follow를 toggle할 대상유저
    target_user = get_object_or_404(User, pk=user_pk)
    # 요청 유저 (로그인한 유저)의 follow_toggle()메서드 실행
    request.user.follow_toggle(target_user)
    # next가 있으면 해당 위치로 아닐경우 target_user의 profile페이지로 이동
    if next:
        return redirect(next)
    return redirect('member:profile', user_pk=user_pk)
