# main.py
import requests
from bs4 import BeautifulSoup
import os
import time

# --- 설정 ---
# 1. 스캔할 갤러리 (만화 갤러리 6 - 개념글)
TARGET_GALLERY_URL = "https://gall.dcinside.com/board/lists/?id=comic_new6&exception_mode=recommend"
# 2. 스캔할 페이지 수 (개념글은 1~2페이지만 해도 충분할 수 있습니다)
PAGES_TO_SCAN = 2
# 3. 알림 보낸 글을 기록할 파일
NOTIFIED_POSTS_FILE = 'notified_posts.txt'
# --- 설정 끝 ---

# 텔레그램 알림 전송 함수
def send_telegram_notification(message):
    """지정된 텔레그램 채널로 메시지를 전송합니다."""
    # GitHub Actions의 'Secrets'에서 토큰과 ID를 가져옴
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    if not TOKEN or not CHAT_ID:
        print("알림: 텔레그램 설정(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)이 완료되지 않았습니다. 콘솔에만 출력합니다.")
        return False

    # 텔레그램 봇 API URL
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status() # 200 OK가 아니면 에러 발생
        if response.json().get("ok"):
            print(f"텔레그램 알림 전송 성공: {message[:20]}...")
            return True
        else:
            print(f"텔레그램 알림 전송 실패: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"오류: 텔레그램 알림 전송에 실패했습니다: {e}")
        return False

# 이미 알림 보낸 게시글 ID 로드
def load_notified_posts():
    """파일에서 이미 알림을 보낸 게시글 ID 목록을 불러옵니다."""
    if not os.path.exists(NOTIFIED_POSTS_FILE):
        return set() # 파일이 없으면 빈 세트(set) 반환
    
    try:
        with open(NOTIFIED_POSTS_FILE, 'r', encoding='utf-8') as f:
            # 파일에서 ID를 읽어와서 set으로 만듦
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"오류: {NOTIFIED_POSTS_FILE} 파일 읽기 실패: {e}")
        return set()

# 알림 보낸 게시글 ID 저장
def save_notified_posts(notified_ids):
    """알림을 보낸 게시글 ID 목록을 파일에 저장합니다."""
    try:
        with open(NOTIFIED_POSTS_FILE, 'w', encoding='utf-8') as f:
            for post_id in notified_ids:
                f.write(f"{post_id}\n")
    except Exception as e:
        print(f"오류: {NOTIFIED_POSTS_FILE} 파일 쓰기 실패: {e}")

# 최신 게시글 긁어오기
def fetch_recent_posts(gallery_url, pages_to_scan):
    """지정된 갤러리의 여러 페이지에서 게시글 목록을 가져옵니다."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    unique_posts = {} # 중복 제거용 딕셔너리 {id: (title, link)}

    print(f"{pages_to_scan}개의 페이지를 스캔합니다: {gallery_url}")

    for page in range(1, pages_to_scan + 1):
        # 1페이지는 page=1, 그 외에는 &page=2, &page=3...
        page_url = f"{gallery_url}&page={page}"
        print(f"  - {page}페이지 확인 중...")
        
        try:
            response = requests.get(page_url, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 게시글 목록 선택 (td.gall_tit a)
            posts = soup.select('td.gall_tit a')
            if not posts:
                print(f"  - {page}페이지에서 게시글을 찾을 수 없습니다.")
                continue

            for post in posts:
                title = post.text.strip()
                link = post.get('href', '')
                
                # [중요] 공지사항, 설문조사, 유저 광고 등 필터링
                # 정상적인 개념글 링크는 /board/view/... 와 no=... 를 포함함
                if not link.startswith('/board/view/') or 'no=' not in link:
                    continue
                
                # 링크에서 게시글 ID (no=...) 추출
                try:
                    # 예: /board/view/?id=comic_new6&no=12345&... -> '12345'
                    post_id = link.split('no=')[1].split('&')[0]
                except (IndexError, AttributeError):
                    continue # ID 추출 실패시 건너뛰기
                
                # 중복되지 않은 글만 추가
                if post_id not in unique_posts:
                    full_link = "https://gall.dcinside.com" + link
                    unique_posts[post_id] = (title, full_link)
                    
        except requests.exceptions.RequestException as e:
            print(f"오류: {page}페이지 접근 실패: {e}")
            continue
        except Exception as e:
            print(f"오류: {page}페이지 파싱 실패: {e}")
            continue
        
        # 페이지 사이에 약간의 텀
        time.sleep(0.1)

    # 딕셔너리를 리스트로 변환하여 반환 (최신 글이 위로 오도록)
    # 갤러리 목록은 이미 최신순이므로 순서를 유지
    return list(unique_posts.items()) # [(id, (title, link)), ...]

# 메인 로직
def main():
    print("--- DC-checker 시작 ---")
    
    # 1. 이전에 알림 보낸 목록 로드 (Artifact로 다운로드된 파일)
    notified_ids = load_notified_posts()
    print(f"이전에 알림 보낸 게시글 수: {len(notified_ids)}")
    
    # 2. 갤러리에서 최신 게시글 가져오기
    recent_posts = fetch_recent_posts(TARGET_GALLERY_URL, PAGES_TO_SCAN)
    if not recent_posts:
        print("새 글을 찾지 못했습니다 (게시글 스캔 실패).")
        print("--- DC-checker 종료 ---")
        return

    new_posts_found = [] # 새로 발견된 글 목록
    
    # 3. 최신 글 목록을 순회하며 '새 글'인지 확인
    # (recent_posts는 최신순이므로, 역순(reversed)으로 돌려야 오래된 글부터 알림이 감)
    for post_id, (title, link) in reversed(recent_posts):
        
        # '새 글' (알림 목록에 없는 글)인지 확인
        if post_id not in notified_ids:
            # (키워드 검사 로직 제거됨 - 모든 새 글을 대상으로 함)
            print(f"발견! -> ID: {post_id}, 제목: {title}")
            new_posts_found.append((post_id, title, link))
            notified_ids.add(post_id) # 알림 목록에 즉시 추가

    # 4. 새로 찾은 글이 있으면 알림 전송
    if new_posts_found:
        print(f"총 {len(new_posts_found)}개의 새 글을 발견하여 알림을 보냅니다.")
        
        # 텔레그램 메시지 생성
        message_lines = []
        for post_id, title, link in new_posts_found:
            message_lines.append(f"[{title}]({link})")
            
        message = "\n".join(message_lines)
        
        # (주의) 텔레그램 메시지 길이 제한 (4096자) 때문에 너무 길면 잘라서 보내야 함
        # 여기서는 한번에 보낸다고 가정
        if len(message) > 4000:
             message = message[:4000] + "\n... (메시지 너무 김)"

        send_telegram_notification(message)
        
        # 5. [중요] 새 ID가 추가된 목록을 파일에 저장 (Artifact로 업로드될 파일)
        save_notified_posts(notified_ids)
        
    else:
        print("새 글을 찾지 못했습니다.")

    print("--- DC-checker 종료 ---")

if __name__ == "__main__":
    main()

