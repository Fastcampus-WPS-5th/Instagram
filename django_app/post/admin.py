from django.contrib import admin
from .models import Post


# Post에 대한 ModelAdmin을 만들고 register
# 이후 /admin에 가서 Post확인하고 사진 첨부
class PostAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
