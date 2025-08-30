import requests
from bs4 import BeautifulSoup

def get_dynamic_values(response_text):
    """HTML에서 동적 값들을 추출"""
    soup = BeautifulSoup(response_text, 'html.parser')
    
    def get_value(tag_name, attr_name):
        tag = soup.find('input', {'name': tag_name})
        return tag[attr_name] if tag and tag.has_attr(attr_name) else None

    return {
        'check_6': get_value('check_6', 'value'),
        'check_7': get_value('check_7', 'value'),
        'check_8': get_value('check_8', 'value'),
        'check_9': get_value('check_9', 'value'),
        'check_10': get_value('check_10', 'value'),
        'c_r_k_x_z': get_value('c_r_k_x_z', 'value'),
        'cur_t': get_value('cur_t', 'value'),
        'service_code': get_value('service_code', 'value'),
        '_GALLTYPE_': 'G'
    }

# 세션 생성
session = requests.Session()

# 갤러리 정보
gallery_id = 'leagueoflegends6'
post_no = '2614521'
view_url = f'https://gall.dcinside.com/board/view/?id={gallery_id}&no={post_no}'

# GET 요청 헤더
get_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'Sec-Ch-Ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

print(f"게시물 페이지에 접속합니다: {view_url}")
try:
    response = session.get(view_url, headers=get_headers)
    response.raise_for_status()
    print("페이지 접속 성공")

    dynamic_values = get_dynamic_values(response.text)
    if not all(dynamic_values.values()):
        print("동적 값 추출 실패")
        exit()

    # POST 요청 헤더
    post_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://gall.dcinside.com',
        'Referer': view_url,
        'Sec-Ch-Ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # POST 요청 데이터
    payload = {
        'id': gallery_id,
        'no': post_no,
        'reply_no': 'undefined',
        'name': 'ㅇㅇ',
        'password': '0000',
        'memo': '아니 이 메모가 어때서 이게 내용 불량이 사유가 되는건데?',
        'recommend': '0',
        'c_gall_id': gallery_id,
        'c_gall_no': post_no,
        'g-recaptcha-response': '',
        '_GALLTYPE_': 'G',
        'headTail': '""',
        'gall_nick_name': 'ㅇㅇ',
        'use_gall_nick': 'N',
        't_vch2': '',
        't_vch2_chk': ''
    }
    
    # 동적 값 추가
    payload.update(dynamic_values)

    # 댓글 작성 요청
    post_url = 'https://gall.dcinside.com/board/forms/comment_submit'
    post_response = session.post(post_url, headers=post_headers, data=payload)
    post_response.raise_for_status()
    
    print("\n응답 결과:")
    print(f"상태 코드: {post_response.status_code}")
    print("응답 내용:")
    print(post_response.text)

except requests.RequestException as e:
    print(f"오류 발생: {e}")