import requests
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

# --- 설정 ---

# 1. 모니터링할 갤러리 URL (기본 URL, &page= 제외)
TARGET_GALLERY_URL = "https://gall.dcinside.com/board/lists/?id=cartoon"

# 2. 찾고 싶은 키워드 목록
TARGET_KEYWORDS = ["후기", "[5]", "냉혹한"] # 원하는 키워드로 수정하세요

# 3. (추가) 한 번에 확인할 페이지 수 (글 리젠이 빠르므로 1~3 페이지 확인)
PAGES_TO_SCAN = 3 

# 4. (중요) 게시글 제목을 포함하는 요소의 CSS 선택자
CSS_SELECTOR_FOR_POSTS = "td.gall_tit a"

# 5. 이미 알림을 보낸 게시글을 기록할 파일
NOTIFIED_POSTS_FILE = "notified_posts.txt"

# 6. (선택) 이메일 알림 설정 (GitHub Actions Secrets에서 가져옴)
SMTP_SERVER = os.environ.get("SMTP_SERVER") 
SMTP_PORT = os.environ.get("SMTP_PORT")     
SENDER_EMAIL = os.environ.get("SENDER_EMAIL") 
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD") 
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") 

# --- /설정 ---


def fetch_recent_posts():
    """갤러리에서 최신 게시글 목록을 가져옵니다. (여러 페이지 스캔)"""
    print(f"{PAGES_TO_SCAN}개의 페이지를 스캔합니다: {TARGET_GALLERY_URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_found_posts = []
    
    try:
        # 1페이지부터 PAGES_TO_SCAN 페이지까지 순회
        for page in range(1, PAGES_TO_SCAN + 1):
            url = f"{TARGET_GALLERY_URL}&page={page}"
            print(f"  - {page}페이지 확인 중...")
            
            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            post_elements = soup.select(CSS_SELECTOR_FOR_POSTS)
            
            if not post_elements and page == 1:
                # 1페이지에서조차 글을 못찾으면 선택자 문제
                print(f"경고: CSS 선택자 '{CSS_SELECTOR_FOR_POSTS}'로 게시글을 찾을 수 없습니다.")
                print("README의 'CSS 선택자 찾기'를 참고하여 선택자를 수정하세요.")
                return []
            
            page_posts = []
            for el in post_elements:
                title = el.get_text(strip=True)
                post_url = el.get('href', '')
                if not post_url.startswith('http'):
                    post_url = "https://gall.dcinside.com" + post_url
                    
                post_id = post_url.split('no=')[-1].split('&')[0]
                
                if post_id:
                    page_posts.append({'id': post_id, 'title': title, 'url': post_url})
            
            all_found_posts.extend(page_posts)
            time.sleep(0.5) # 페이지 사이에 약간의 딜레이

        # 중복 제거 (여러 페이지에 공지 등이 중복으로 나올 경우 대비)
        unique_posts = []
        seen_ids = set()
        for post in all_found_posts:
            if post['id'] not in seen_ids:
                unique_posts.append(post)
                seen_ids.add(post['id'])
        
        return unique_posts

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져오는 데 실패했습니다 - {e}")
        return []

def load_notified_posts():
    """이미 알림을 보낸 게시글 ID 목록을 파일에서 불러옵니다."""
# ... (이하 코드는 이전과 동일) ...
    if not os.path.exists(NOTIFIED_POSTS_FILE):
# ... (이하 코드는 이전과 동일) ...
    
    with open(NOTIFIED_POSTS_FILE, 'r', encoding='utf-8') as f:
# ... (이하 코드는 이전과 동일) ...

def save_notified_post(post_id):
    """알림을 보낸 게시글 ID를 파일에 추가합니다."""
# ... (이하 코드는 이전과 동일) ...
        f.write(post_id + '\n')

def send_email_notification(post):
    """이메일로 알림을 보냅니다."""
# ... (이하 코드는 이전과 동일) ...
    if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
# ... (이하 코드는 이전과 동일) ...
        return

    try:
# ... (이하 코드는 이전과 동일) ...
        subject = f"[DC-checker] 새 글 알림: {post['title']}"
# ... (이하 코드는 이전과 동일) ...
        body += f"링크: {post['url']}\n"

# ... (이하 코드는 이전과 동일) ...
        msg = MIMEText(body, 'plain', 'utf-8')
# ... (이하 코드는 이전과 동일) ...
        msg['To'] = RECEIVER_EMAIL

# ... (이하 코드는 이전과 동일) ...
        print(f"SMTP 서버({SMTP_SERVER}:{SMTP_PORT})에 연결 중...")
# ... (이하 코드는 이전과 동일) ...
            s.starttls() # TLS 암호화 시작
# ... (이하 코드는 이전과 동일) ...
            s.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
# ... (이하 코드는 이전과 동일) ...
        print(f"알림: 이메일({RECEIVER_EMAIL})로 알림을 성공적으로 보냈습니다. (ID: {post['id']})")

    except smtplib.SMTPAuthenticationError:
# ... (이하 코드는 이전과 동일) ...
        print("SENDER_EMAIL 또는 SENDER_PASSWORD(앱 비밀번호)가 올바른지 확인하세요.")
# ... (이하 코드는 이전과 동일) ...
        print(f"오류: 이메일 전송에 실패했습니다 - {e}")


def main():
    print("--- DC-checker 시작 ---")
    
# ... (이하 코드는 이전과 동일) ...
    recent_posts = fetch_recent_posts()
# ... (이하 코드는 이전과 동일) ...
        print("--- DC-checker 종료 ---")
        return

# ... (이하 코드는 이전과 동일) ...
    notified_ids = load_notified_posts()
    
# ... (이하 코드는 이전과 동일) ...
    new_posts_found = []
    
    for post in recent_posts:
# ... (이하 코드는 이전과 동일) ...
            for keyword in TARGET_KEYWORDS:
# ... (이하 코드는 이전과 동일) ...
                    new_posts_found.append(post)
                    break 

# ... (이하 코드는 이전과 동일) ...
    if not new_posts_found:
# ... (이하 코드는 이전과 동일) ...
    else:
        for post in new_posts_found:
# ... (이하 코드는 이전과 동일) ...
            # 이메일 알림 보내기
            send_email_notification(post)
# ... (이하 코드는 이전과 동일) ...
            time.sleep(1) 

    print("--- DC-checker 종료 ---")

if __name__ == "__main__":
    main()

