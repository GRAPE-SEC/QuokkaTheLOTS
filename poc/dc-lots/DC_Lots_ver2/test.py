import requests

# 1. 요청을 보낼 URL
url = 'https://gall.dcinside.com/board/forms/comment_submit'

# 2. HTTP 요청 헤더 설정
#    - User-Agent, Referer 등은 서버가 정상적인 브라우저 접근으로 인식하게 하기 위해 중요합니다.
#    - Content-Length, Host 등은 requests 라이브러리가 자동으로 관리하므로 직접 넣지 않아도 됩니다.
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'cto_bundle=KBdVcV9VZ3JtRDhPemFlZCUyQkJUZTdjeDhSR3JrMFRyNUhDT1lVWGFNTXRuYUp6JTJGJTJCMGxoNlJVeENTUmJ5JTJCJTJCZmp5c3JxMGg5NlhKSDZ2VlZnJTJGZVB6ODFWM3ZJclZsWlhkVUtuSlh5Y25ERGpNVzclMkJKWkhOWEE2QWlnMnFVJTJCZ3NZdlBYVUtacjJlMFRlZEV3bklhNDRIek0wZFVRJTNEJTNE',
    'Origin': 'https://gall.dcinside.com',
    'Referer': 'https://gall.dcinside.com/board/view/?id=leagueoflegends6&no=2614521&page=107261',
    'Sec-Ch-Ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

# 3. 전송할 데이터 (Payload) 설정
#    - 'ㅇㅇ'와 같이 한글로 된 부분은 원래 인코딩된 값('%E3%85%87%E3%85%87')을 사용해도 되지만,
#      requests가 알아서 인코딩해주므로 가독성 좋게 한글로 작성하는 것이 편리합니다.
payload = {
    'id': 'leagueoflegends6',
    'no': '2614521',
    'reply_no': 'undefined',
    'name': 'ㅇㅇ',
    'password': '0000',
    'memo': 'ㅇㅇ',
    'cur_t': '1756545638',
    'check_6': 'eb15f2555a403ca1080a5a48dcb478f8dfeffb42026796fdad9e497eb1eefb167d991a0f208af9e456',
    'check_7': '30',
    'check_8': 'e320dc5c674f',
    'check_9': '3191758cdbe62b75b39c84',
    'check_10': '3295698bcff82460af9396f047aea5587a7c12',
    'recommend': '0',
    'c_r_k_x_z': '7cea8570b0866df03de7e8e04f9f7773c487d96d6c270629d976f647094a4ff6',
    't_vch2': '',
    't_vch2_chk': '',
    'c_gall_id': 'leagueoflegends6',
    'c_gall_no': '2614521',
    'service_code': '21ac6d96ad152e8f15a05b7350a2475909d19bcedeba9d4face8115e9bc0fa4c020694bd9b1e1289786e4fd3b4566fe965ead366cca5cb90fc67c85ea7302cf538840d5470fbc2cf200a2bc762a476f5fc61dff1bcc75c29c80466651866644d73001a808f47592f781d5948853a72801d80f8d56a1ca19b66d24bab04fe8d5184fe00a1ad48348c78227397ff05f337b733d780e72f21f619fbbb6c2a640d5dabe5c4df74064d03c48f1eb34d465eb066330deb240979c4606d0a71a51bef600de627fa6354926b6ed4a1e02e7fac8f',
    'g-recaptcha-response': '',
    '_GALLTYPE_': 'G',
    'headTail': '""',
    'gall_nick_name': '롤갤러',
    'use_gall_nick': 'N'
}

# 4. POST 요청 보내기
try:
    response = requests.post(url, headers=headers, data=payload)
    
    # 5. 응답 확인
    print(f"Status Code: {response.status_code}") # 상태 코드 (200이면 성공)
    print("Response Body:")
    print(response.text) # 서버로부터 받은 응답 내용

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")