# 파일 유출 POC (via Discord Webhook)

## 목적 : 사용자 디렉토리 내의 특정 확장자 파일(.txt, .docx, .pdf)을 찾아  Discord Wehook을 통해 외부로 유출

- 터미널에서 python3 file.exfiltratoin.py 실행하면 ~/Downloads에 있는 .txt, .pdf, .docx 파일이 지정한 discord 채널로 전송됨

## 문제점 : Download 폴더의 지정 확장자만 유출할 수 있음. Discord Webhook는 8MB 파일 크키 제한이 있음. 

## 추후 개선 방향 : ~/Desktop, ~/Documents 등을 추가로 탐색해서 경로 확장하기. .png, .xlsx 등의 확장자 확장하기. time.sleep() 기반 루프를 넣어서 주기적으로 탐색하게 하기. 