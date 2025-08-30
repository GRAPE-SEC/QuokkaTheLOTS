## 본래 짜던 코드에서 비공식 확장 프로그램으로 규정되어 실행이 안되 완전 리셋하고 코드를 다시 짜는 중인데 아래와 같이 댓글 다는 것을 테스트 해보아도 안되어 1차 종료...


import requests
import base64
import time
import hashlib
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import re

def parse_url_params(url):
    """URL에서 id, no, page 추출"""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return {
        'id': qs.get('id', [''])[0],
        'no': qs.get('no', [''])[0],
        'page': qs.get('page', [''])[0]
    }

def extract_value_from_html(html, element_id=None, name=None, regex=None):
    """HTML에서 특정 값 추출"""
    soup = BeautifulSoup(html, 'html.parser')
    if element_id:
        tag = soup.find('input', {'id': element_id})
        if tag and tag.has_attr('value'):
            return tag['value']
    if name:
        tag = soup.find('input', {'name': name})
        if tag and tag.has_attr('value'):
            return tag['value']
    if regex:
        match = re.search(regex, html)
        if match:
            return match.group(1)
    return None

def fetch_required_data(url):
    """페이지 접속에 필요한 데이터 수집"""
    session = requests.Session()
    headers = {
        "Host": "gall.dcinside.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": url,
        "Connection": "keep-alive"
    }
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        cookies = session.cookies.get_dict()

        # 필요한 추가 쿠키를 수동으로 설정
        additional_cookies = {
            "ck_img_view_cnt": "1",
            "daum_ad": "Y",
            "alarm_popup": "1",
            "last_alarm": str(int(time.time()))
        }
        cookies.update(additional_cookies)

        esno = extract_value_from_html(res.text, element_id="e_s_n_o")
        service_code = extract_value_from_html(res.text, name="service_code")
        return {
            "cookies": cookies,
            "esno": esno,
            "service_code": service_code
        }
    except requests.RequestException as e:
        print(f"[!] 네트워크 요청 오류: {e}")
        return {"cookies": {}, "esno": None, "service_code": None}

def generate_checks():
    """댓글 작성에 필요한 check 값들 생성"""
    cur_t = str(int(time.time()))
    return {
        'cur_t': cur_t,
        'check_6': hashlib.md5((cur_t + "salt").encode()).hexdigest(),
        'check_7': "30",
        'check_8': hashlib.md5(cur_t[:5].encode()).hexdigest()[:12],
        'check_9': hashlib.md5(cur_t.encode()).hexdigest()[:20],
        'check_10': hashlib.md5((cur_t + "key").encode()).hexdigest()[:30]
    }

def post_comment(url, service_code, memo, cookies, password="0000", name="ㅇㅇ", gall_nick_name="롤갤러", use_gall_nick="N"):
    """댓글 등록"""
    post_url = "https://gall.dcinside.com/board/forms/comment_submit"
    headers = {
        "Host": "gall.dcinside.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": url,
        "Connection": "keep-alive"
    }
    checks = generate_checks()
    payload = {
        "id": url.split("id=")[-1].split("&")[0],
        "no": url.split("no=")[-1].split("&")[0],
        "memo": memo,
        "service_code": service_code,
        "password": password,
        "name": name,
        "cur_t": checks['cur_t'],
        "check_6": checks['check_6'],
        "check_7": checks['check_7'],
        "check_8": checks['check_8'],
        "check_9": checks['check_9'],
        "check_10": checks['check_10'],
        "gall_nick_name": gall_nick_name,
        "use_gall_nick": use_gall_nick
    }
    try:
        res = requests.post(post_url, headers=headers, data=payload, cookies=cookies, timeout=10)
        res.raise_for_status()
        return res.text
    except requests.RequestException as e:
        print(f"[!] 댓글 등록 오류: {e}")
        return None

def main():
    url = "https://gall.dcinside.com/board/view/?id=leagueoflegends6&no=2614521&page=107261"
    data = fetch_required_data(url)
    cookies = data["cookies"]
    service_code = data["service_code"]

    # 쿠키 검증
    print("[*] 획득한 쿠키:", cookies)
    
    # 댓글 작성 테스트
    memo = "테스트 댓글입니다."
    password = "0000"
    name = "ㅇㅇ"
    gall_nick_name = "롤갤러"
    use_gall_nick = "N"
    response = post_comment(url, service_code, memo, cookies, password, name, gall_nick_name, use_gall_nick)
    print("[*] 댓글 작성 응답:", response)

if __name__ == "__main__":
    main()