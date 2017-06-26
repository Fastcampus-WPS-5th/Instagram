from django.shortcuts import render

__all__ = (
    'youtube_search',
)


def youtube_search(request):
    return render(request, 'post/youtube_search.html')
