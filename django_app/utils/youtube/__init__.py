import requests
from googleapiclient.discovery import build


def search_original(q):
    url_api_search = 'https://www.googleapis.com/youtube/v3/search'
    search_params = {
        'part': 'snippet',
        'key': 'AIzaSyACCLlnn_hlOpNk5XUBpRqs-iZWpbTm-J4',
        'maxResults': '10',
        'type': 'video',
        'q': q,
    }
    # YouTube의 search api에 요청, 응답 받음
    response = requests.get(url_api_search, params=search_params)
    # 응답은 JSON형태로 오며, json()메서드로 파이썬 객체 형식으로 변환
    data = response.json()
    return data


def search(q):
    DEVELOPER_KEY = "AIzaSyACCLlnn_hlOpNk5XUBpRqs-iZWpbTm-J4"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY
    )

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=q,
        part="id,snippet",
        maxResults=10,
        type='video',
    ).execute()
    return search_response
