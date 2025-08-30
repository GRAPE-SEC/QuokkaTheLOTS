import requests
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

if __name__ == "__main__":
    test_url = "https://gall.dcinside.com/board/view/?id=leagueoflegends6&no=2614521&page=107261"
    data = fetch_required_data(test_url)
    print("필수 데이터:", data)