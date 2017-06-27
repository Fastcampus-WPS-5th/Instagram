import requests


def search(q):
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
