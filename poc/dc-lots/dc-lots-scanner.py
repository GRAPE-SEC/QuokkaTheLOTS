import aiohttp
import asyncio
from bs4 import BeautifulSoup
import random
from datetime import datetime
import re

# 설정
GALLERY_ID = 'leagueoflegends6'
LIST_URL = f'https://gall.dcinside.com/board/lists/?id={GALLERY_ID}&page='
MAX_RESULTS = 3
CONCURRENCY = 5  # 더 빠른 동시 처리

# 로그 파일 초기화
start_time = datetime.now()
log_filename = f'dc_lots_log_{start_time.strftime("%Y_%m_%d")}.txt'

def log(message: str):
    print(message)
    with open(log_filename, 'a', encoding='utf-8') as f:
        f.write(message.strip() + '\n')

def extract_gallog_url(post_tag):
    img = post_tag.select_one('.writer_nikcon img[onclick*="gallog.dcinside.com"]')
    if img and 'onclick' in img.attrs:
        onclick = img['onclick']
        m = re.search(r"window\.open\('(?P<url>[^']+)'", onclick)
        if m:
            href = m.group('url')
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://gallog.dcinside.com' + href
            elif not href.startswith('http'):
                href = 'https://' + href
            return href
    return None

async def is_deleted_gallog(session, gallog_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://gall.dcinside.com/',
        }
        async with session.get(gallog_url, headers=headers, allow_redirects=True, timeout=10) as resp:
            final_url = str(resp.url)
            return '/deleted' in final_url or resp.status == 404
    except Exception as e:
        log(f'[!] 갤로그 확인 중 오류: {gallog_url} - {e}')
        return False

def extract_post_url(post_tag):
    link = post_tag.select_one('.gall_tit a')
    if link:
        return 'https://gall.dcinside.com' + link['href']
    return None

def get_comment_count(post_tag):
    comment_tag = post_tag.select_one('.gall_tit .reply_numb')
    if comment_tag:
        try:
            return int(comment_tag.text.strip('[]'))
        except:
            return 0
    return 0

async def fetch_page(session, page, semaphore, candidates, seen, stop_event):
    url = LIST_URL + str(page)
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    async with semaphore:
        try:
            if stop_event.is_set():
                return

            log(f'[*] 페이지 {page} 처리 중... (현재 후보 수: {len(candidates)})')

            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    log(f'[!] 페이지 {page} 요청 실패 (상태 코드: {response.status})')
                    return

                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                posts = soup.select('tr.ub-content')

                for post in posts:
                    if stop_event.is_set():
                        return

                    gallog_url = extract_gallog_url(post)
                    if not gallog_url:
                        continue

                    if await is_deleted_gallog(session, gallog_url) and get_comment_count(post) == 0:
                        post_url = extract_post_url(post)
                        title_tag = post.select_one('.gall_tit')
                        date_tag = post.select_one('.gall_date')
                        if not post_url or not title_tag or not date_tag:
                            continue
                        # 줄바꿈 제거
                        title = title_tag.text.strip().replace('\n', ' ').replace('\r', ' ')
                        date = date_tag.text.strip()

                        key = (title, post_url)
                        if key in seen:
                            continue

                        seen.add(key)
                        candidates.append((title, post_url, date, page))
                        log(f'[후보] (p.{page}) {date} | {title} | {post_url}')

                        if len(candidates) >= MAX_RESULTS:
                            stop_event.set()
                            return

        except Exception as e:
            import traceback
            log(f'[!] 페이지 {page} 처리 중 오류 발생: {e}\n{traceback.format_exc()}')

        await asyncio.sleep(random.uniform(2.0, 3.0))

async def get_total_pages():
    url = LIST_URL + '1'
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as res:
            text = await res.text()
            soup = BeautifulSoup(text, 'html.parser')
            total_page_tag = soup.select_one('span.num.total_page')
            if total_page_tag:
                return int(total_page_tag.text.strip())
            else:
                raise Exception('전체 페이지 수를 가져오지 못했습니다.')

async def main():
    log('==========================================')
    log('[*] 디시인사이드 LOTS용 게시물 자동 스캐너 시작')
    log(f'[*] 시작 시각: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    log(f'[*] 대상 갤러리: {GALLERY_ID}')

    total_pages = await get_total_pages()
    log(f'[+] 전체 페이지 수: {total_pages}')

    start_page = int(total_pages - (total_pages / 3))
    end_page = int(total_pages - (total_pages / 6))
    if start_page > end_page:
        start_page, end_page = end_page, start_page
    log(f'[+] 탐색 범위: {start_page} ~ {end_page}')

    candidates = []
    seen = set()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    stop_event = asyncio.Event()

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=CONCURRENCY)) as session:
        tasks = [
            fetch_page(session, page, semaphore, candidates, seen, stop_event)
            for page in range(start_page, end_page + 1)
        ]
        await asyncio.gather(*tasks)

    log('\n[LOTS용 후보 게시물 요약]')
    for idx, (title, url, date, page) in enumerate(candidates, 1):
        clean_title = title.replace('\n', ' ').replace('\r', ' ')
        log(f'{idx}. (p.{page}) {date} | {clean_title} | {url}')
    log('[*] 스캔 종료')

if __name__ == '__main__':
    asyncio.run(main())
