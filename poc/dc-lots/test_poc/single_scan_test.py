import requests

def test_gallog_redirect(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36',
            'Referer': 'https://gall.dcinside.com/'
        }
        resp = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        print(f'요청 URL: {url}')
        print(f'최종 URL: {resp.url}')
        print(f'HTTP 상태 코드: {resp.status_code}')
        print('리다이렉트 내역:')
        for r in resp.history:
            print(f'  {r.status_code} -> {r.url}')
        if '/deleted' in resp.url:
            print('[*] 탈퇴 계정으로 판별됨')
        else:
            print('[*] 정상 계정 또는 판별 불가')
    except Exception as e:
        print(f'[!] 요청 중 오류: {e}')

if __name__ == '__main__':
    test_url = 'https://gallog.dcinside.com/event0950'
    test_gallog_redirect(test_url)