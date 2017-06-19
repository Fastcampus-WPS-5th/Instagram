from django import forms

from ..models import Post


class PostForm(forms.ModelForm):
    # 생성자를 조작해서 실제 Post의 photo필드는 blank=True
    #   (Form에서 required=False)이지만,
    #   Form을 사용할때는 반드시 photo를 받도록 함
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo'].required = True

    comment = forms.CharField(
        required=False,
        widget=forms.TextInput
    )

    class Meta:
        model = Post
        fields = (
            'photo',
            'comment',
        )

    def save(self, **kwargs):
        # 전달된 키워드인수중 'commit'키 값을 가져옴
        commit = kwargs.get('commit', True)
        # 전달된 키워드인수중 'author'키 값을 가져오고, 기존 kwargs dict에서 제외
        author = kwargs.pop('author', None)

        # super()의 save()호출
        self.instance.author = author
        instance = super().save(**kwargs)

        # commit인수가 True이며 comment필드가 채워져 있을 경우 Comment생성 로직을 진행
        #   (이 위에서 super().save()를 실행하기 때문에
        #       현재위치에서는 author나 pk에 대한 검증이 끝난 상태)
        comment_string = self.cleaned_data['comment']
        if commit and comment_string:
            # RelatedManager를 이용해 Comment객체 생성 및 저장
            instance.comment_set.create(
                author=instance.author,
                content=comment_string
            )
        # ModelForm의 save()에서 반환해야 하는 model의 instance리턴
        return instance
