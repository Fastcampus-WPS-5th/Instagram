from django import template

register = template.Library()


# 실제 템플릿에서 사용할 수 있도록 template.Library의 filter 데코레이터 적용
@register.filter
def query_string(q):
    # q에는 QueryDict가 온다
    # str.join()과 리스트 컴프리헨션으로 한줄로 줄여보세요
    # ret = '?'
    # for k, v_list in q.lists():
    #     for v in v_list:
    #         ret += '&{}={}'.format(k, v)
    # return ret
    return '?' + '&'.join(['{}={}'.format(k, v) for k, v_list in q.lists() for v in v_list])
