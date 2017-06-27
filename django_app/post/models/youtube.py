from django.db import models

__all__ = (
    'Video',
)


# Video를 위한 CustomManager
class VideoManager(models.Manager):
    def create_from_search_result(self, result):
        """
        :param result: YouTube Search API를 사용 후, 검색 결과에서 'items'리스트의 각 항목
        :return: Video object
        """
        # Video객체를 만들기 위해 필요한 정보 꺼내옴
        youtube_id = result['id']['videoId']
        title = result['snippet']['title']
        description = result['snippet']['description']
        url_thumbnail = result['snippet']['thumbnails']['high']['url']
        # get_or_create를 이용해 youtube_id에 해당하는 데이터가 있으면 넘어가고, 없으면 생성
        video, video_created = self.get_or_create(
            youtube_id=youtube_id,
            defaults={
                'title': title,
                'description': description,
                'url_thumbnail': url_thumbnail
            }
        )
        print('Video({}) is {}'.format(
            video.title,
            'created' if video_created else 'already exist'
        ))
        return video


class Video(models.Model):
    youtube_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url_thumbnail = models.CharField(max_length=200)

    objects = VideoManager()

    def __str__(self):
        return self.title
