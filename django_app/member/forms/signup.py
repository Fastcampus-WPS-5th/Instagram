from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupForm(forms.Form):
    # SignupForm을 구성하고 해당 form을 view에서 사용하도록 설정
    username = forms.CharField(
        widget=forms.TextInput
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput
    )

    # clean_<fieldname>메서드를 사용해서
    # username필드에 대한 유효성 검증을 실행
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'Username already exist'
            )
        return username
