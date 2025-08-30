import requests
from dc_Lots_required_data import fetch_required_data, parse_url_params

def fetch_comments(url):
    """댓글 데이터 가져오기"""
    data = fetch_required_data(url)
    cookies = data["cookies"]
    esno = data["esno"]
    if not esno:
        print("[!] e_s_n_o 값 누락")
        return None

    post_url = "https://gall.dcinside.com/board/comment/"
    headers = {
        "Host": "gall.dcinside.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": url,
        "Connection": "keep-alive"
    }
    params = parse_url_params(url)
    payload = {
        "id": params['id'],
        "no": params['no'],
        "e_s_n_o": esno,
        "comment_page": 1,
        "sort": "D"
    }
    try:
        res = requests.post(post_url, headers=headers, data=payload, cookies=cookies, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"[!] 댓글 요청 오류: {e}")
        return None

def print_comments_pretty(comments_json):
    """댓글 데이터 출력"""
    if not comments_json or "comments" not in comments_json:
        print("[!] 댓글 데이터가 없습니다.")
        return
    print(f"총 댓글 수: {comments_json.get('total_cnt', 0)}")
    for cmt in comments_json["comments"]:
        nick = cmt.get("name", "")
        if nick == "댓글돌이":
            continue  # 봇 댓글은 출력하지 않음
        memo = cmt.get("memo", "")
        reg_date = cmt.get("reg_date", "")
        print(f"[{nick}] {memo} ({reg_date})")

if __name__ == "__main__":
    test_url = "https://gall.dcinside.com/board/view/?id=leagueoflegends6&no=2614521&page=107261"
    comments_json = fetch_comments(test_url)
    print_comments_pretty(comments_json)