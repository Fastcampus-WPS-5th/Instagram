from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_POST

from post.decorators import post_owner
from post.forms import CommentForm
from ..forms import PostForm
from ..models import Post, Tag

# 자동으로 Django에서 인증에 사용하는 User모델클래스를 리턴
#   https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#django.contrib.auth.get_user_model
User = get_user_model()

__all__ = (
    'post_list',
    'post_detail',
    'post_create',
    'post_modify',
    'post_delete',
    'post_like_toggle',
    'hashtag_post_list',
)
# 1. EMAIL관련 settings.py에 추가
# 2. 누군가 어떤 글에 댓글을 달면, 해당 글의 작성자 이메일로 "누가 어떤내용의 댓글을 달았음"이라는 메일 보내기


def post_list_original(request):
    # 모든 Post목록을 'posts'라는 key로 context에 담아 return render처리
    # post/post_list.html을 template으로 사용하도록 한다

    # 각 포스트에 대해 최대 4개까지의 댓글을 보여주도록 템플릿에 설정
    # 각 post하나당 CommentForm을 하나씩 가지도록 리스트 컴프리헨션 사용

    # 숙제
    # 1. post_list와 hashtag_post_list에서 pagination을 이용해서
    #    한 번에 10개씩만 표시하도록 수정
    #   https://docs.djangoproject.com/en/1.11/topics/pagination/
    # 2. 좋아요 버튼 구현 및 좋아요 한 사람 목록 출력
    posts = Post.objects.all()
    context = {
        'posts': posts,
        'comment_form': CommentForm(),
    }
    return render(request, 'post/post_list.html', context)


def post_list(request):
    # 전체 Post목록 QuerySet생성 (아직 평가되지 않음)
    all_posts = Post.objects.all()
    # Paginator객체 생성, 한 페이지당 3개씩
    p = Paginator(all_posts, 3)

    # GET parameter에서 'page'값을 page_num변수에 할당
    page_num = request.GET.get('page')

    # Paginator객체에서 page메서드로 page_num변수를 인수로 전달하여 호출
    try:
        posts = p.page(page_num)

    # 만약 page_num변수가 int형으로 변환이 불가능하면
    except PageNotAnInteger:
        # 1페이지에 해당하는 Post object list를 posts에 할당
        posts = p.page(1)
    # 만약 page_num에 객체가 없을 경우 (빈 페이지)
    except EmptyPage:
        # 마지막 페이지에 해당하는 Post object list를 posts에 할당
        posts = p.page(p.num_pages)

    # render에 사용할 dict객체
    context = {
        'posts': posts,
        # 'comment_form': CommentForm(),
        'comment_form': CommentForm(auto_id=False),
    }
    return render(request, 'post/post_list.html', context)


def post_detail(request, post_pk):
    # Model(DB)에서 post_pk에 해당하는 Post객체를 가져와 변수에 할당
    # ModelManager의 get메서드를 사용해서 단 한개의 객체만 가져온다
    # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#get

    # 가져오는 과정에서 예외처리를 한다 (Model.DoesNotExist)
    try:
        post = Post.objects.get(pk=post_pk)
    except Post.DoesNotExist:
        # 1. 404 Notfound를 띄워준다
        # return HttpResponseNotFound('Post not found, detail: {}'.format(e))

        # 2. post_list view로 돌아간다
        # 2-1. redirect를 사용
        #   https://docs.djangoproject.com/en/1.11/topics/http/shortcuts/#redirect
        # return redirect('post:post_list')
        # 2-2. HttpResponseRedirect
        #   https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponseRedirect
        url = reverse('post:post_list')
        return HttpResponseRedirect(url)

    # request에 대해 response를 돌려줄때는 HttpResponse나 render를 사용가능
    # template을 사용하려면 render함수를 사용한다
    # render함수는
    #   django.template.loader.get_template함수와
    #   django.http.HttpResponse함수를 축약해 놓은 shortcut이다
    #       https://docs.djangoproject.com/en/1.11/topics/http/shortcuts/#render

    # ! 이 뷰에서는 render를 사용하지 않고, 전체 과정(loader, HttpResponse)을 기술
    # Django가 템플릿을 검색할 수 있는 모든 디렉토리를 순회하며
    # 인자로 주어진 문자열값과 일치하는 템플릿이 있는지 확인 후,
    # 결과를 리턴 (django.template.backends.django.Template클래스형 객체)
    # get_template()메서드
    #   https://docs.djangoproject.com/en/1.11/topics/templates/#django.template.loader.get_template
    template = loader.get_template('post/post_detail.html')
    # dict형 변수 context의 'post'키에 post(Post객체)를 할당
    context = {
        # context로 전달될 dict의 "키"값이 템플릿에서 사용가능한 변수명이 됨
        'post': post,
    }
    # template에 인자로 주어진 context, request를 render함수를 사용해서 해당 template을 string으로 변환
    rendered_string = template.render(context=context, request=request)
    # 변환된 string을 HttpResponse형태로 돌려준다
    return HttpResponse(rendered_string)


@login_required
def post_create(request):
    # POST요청을 받아 Post객체를 생성 후 post_list페이지로 redirect
    if request.method == 'POST':
        ### PostForm을 쓰지 않은경우
        # # get_user_model을 이용해서 얻은 User클래스(Django에서 인증에 사용하는 유저모델)에서 임의의 유저 한명을 가져온다.
        # user = User.objects.first()
        # # 새 Post객체를 생성하고 DB에 저장
        # post = Post.objects.create(
        #     author=user,
        #     # request.FILES에서 파일 가져오기
        #     #   https://docs.djangoproject.com/en/1.11/topics/http/file-uploads/#basic-file-uploads
        #     # 가져온 파일을 ImageField에 넣도록 설정
        #     # 'file'은 POST요청시 input[type="file"]이 가진 name속성
        #     photo=request.FILES['photo'],
        # )
        # # POST요청시 name이 'comment'인 input에서 전달된 값을 가져옴
        # # dict.get()
        # #   https://www.tutorialspoint.com/python/dictionary_get.htm
        # comment_string = request.POST.get('comment', '')
        # # 빈 문자열 ''이나 None모두 False로 평가되므로
        # # if not으로 댓글로 쓸 내용 또는 comment키가 전달되지 않았음을 검사 가능
        # if comment_string:
        #     # 댓글로 사용할 문자열이 전달된 경우 위에서 생성한 post객체에 연결되는 Comment객체를 생성해준다
        #     post.comment_set.create(
        #         # 임의의 user를 사용하므로 나중에 실제 로그인된 사용자로 바꾸어주어야 함
        #         author=user,
        #         content=comment_string,
        #     )
        #     # 역참조로 가져온 RelatedManager를 사용하지 않을경우엔 아래와 같이 작업함
        #     # Comment.objects.create(
        #     #     post=post,
        #     #     author=user,
        #     #     content=comment_string,
        #     # )
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # ModelForm의 save()메서드를 사용해서 Post객체를 가져옴
            post = form.save(author=request.user)
            return redirect('post:post_detail', post_pk=post.pk)
    else:
        # post/post_create.html을 render해서 리턴
        form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'post/post_create.html', context)


@post_owner
@login_required
def post_modify(request, post_pk):
    # 현재 수정하고자하는 Post객체
    post = Post.objects.get(pk=post_pk)

    if request.method == 'POST':
        form = PostForm(data=request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post:post_detail', post_pk=post.pk)
    else:
        form = PostForm(instance=post)
    context = {
        'form': form,
    }
    return render(request, 'post/post_modify.html', context)


@post_owner
@login_required
def post_delete(request, post_pk):
    # post_pk에 해당하는 Post에 대한 delete요청만을 받음
    # 처리완료후에는 post_list페이지로 redirect
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        post.delete()
        return redirect('post:post_list')
    else:
        context = {
            'post': post,
        }
        return render(request, 'post/post_delete.html', context)


@require_POST
@login_required
def post_like_toggle(request, post_pk):
    # 1. post_pk에 해당하는 Post instance를 변수(post)에 할당
    post = get_object_or_404(Post, pk=post_pk)
    # 2. post에서 PostLike로의 RelatedManager를 사용해서
    #       post속성이 post, user속성이 request.user인 PostLike가 있는지 get_or_create
    # M2M필드가 중간자모델을 거치지 않을 경우
    # if request.user not in post.like_users:
    #     post.like_users.add(request.user)

    # 중간자모델을 사용할 경우
    # get_or_create를 사용해서 현재 Post와 request.user에 해당하는 PostLike인스턴스를 가져옴
    post_like, post_like_created = post.postlike_set.get_or_create(
        user=request.user
    )

    # 3. 이후 created여부에 따라 해당 PostLike인스턴스를 삭제 또는 그냥 넘어가기
    # post_like_created가 get_or_create를 통해 새로 PostLike가 만들어졌는지, 아니면 기존에 있었는지 여부를 나타냄
    if not post_like_created:
        # 기존에 PostLike가 있었다면 삭제해준다
        post_like.delete()

    # 4. 리턴주소는 next가 주어질 경우 next, 아닐 경우 post_detail로
    # next = request.GET.get('next')
    # if next:
    #     return redirect(next)
    return redirect('post:post_detail', post_pk=post.pk)


def hashtag_post_list(request, tag_name):
    # 1. template생성
    #   post/hashtag_post_list.html
    #   tag_name과 post_list, post_count변수를 전달받아 출력
    #   tag_name과 post_count는 최상단 제목에 사용
    #   post_list는 순회하며 post_thumbnail에 해당하는 html을 구성해서 보여줌
    #
    # 2. 쿼리셋 작성
    #   특정 tag_name이 해당 Post에 포함된 Comment의 tags에 포함되어있는 Post목록 쿼리 생성
    #        posts = Post.objects.filter()
    #
    # 3. urls.py와 이 view를 연결
    # 4. 해당 쿼리셋을 적절히 리턴
    # 5. Comment의 make_html_and_add_tags()메서드의
    #    a태그를 생성하는 부분에 이 view에 연결되는 URL을 삽입
    tag = get_object_or_404(Tag, name=tag_name)

    # Post에 달린 댓글의 Tag까지 검색할 때
    # posts = Post.objects.filter(comment__tags=tag).distinct()

    # Post의 my_comment에 있는 Tag만 검색할 때
    posts = Post.objects.filter(my_comment__tags=tag)
    posts_count = posts.count()

    context = {
        'tag': tag,
        'posts': posts,
        'posts_count': posts_count,
    }
    return render(request, 'post/hashtag_post_list.html', context)

