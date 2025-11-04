# main.py
import requests
from bs4 import BeautifulSoup
import os
import time

# --- 설정 ---
# 1. 스캔할 갤러리 (만화 갤러리 6 - 개념글)
TARGET_GALLERY_URL = "https://gall.dcinside.com/board/lists/?id=comic_new6&exception_mode=recommend"
# 2. 스캔할 페이지 수
PAGES_TO_SCAN = 1

# 3. [수정됨] 알림 보낸 글을 기록할 파일 이름
NOTIFIED_POSTS_FILENAME = 'notified_posts.txt'
# [수정됨] GitHub Actions의 작업 공간(workspace) 경로를 기준으로 파일 경로 설정
WORKSPACE_PATH = os.environ.get('GITHUB_WORKSPACE', '.')

# [✅ 핵심 수정 1] 아티팩트를 저장할 별도의 .cache 디렉토리 지정
CACHE_DIR = os.path.join(WORKSPACE_PATH, '.cache')
NOTIFIED_POSTS_FILE_PATH = os.path.join(CACHE_DIR, NOTIFIED_POSTS_FILENAME)
# --- 설정 끝 ---


# 텔레그램 알림 전송 함수
def send_telegram_notification(message):
    """지정된 텔레그램 채널로 메시지를 전송합니다."""
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    if not TOKEN or not CHAT_ID:
        print("알림: 텔레그램 설정(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)이 완료되지 않았습니다. 콘솔에만 출력합니다.")
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status() 
        if response.json().get("ok"):
            print(f"텔레그램 알림 전송 성공: {message[:20]}...")
            return True
        else:
            print(f"텔레그램 알림 전송 실패: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"오류: 텔레그램 알림 전송에 실패했습니다: {e}")
        return False

# 이미 알림 보낸 게시글 ID 로드 (경로 수정됨)
def load_notified_posts():
    """파일에서 이미 알림을 보낸 게시글 ID 목록을 불러옵니다."""
    if not os.path.exists(NOTIFIED_POSTS_FILE_PATH):
        print(f"알림: '{NOTIFIED_POSTS_FILE_PATH}' 파일이 없어 새로 시작합니다.")
        return set()
    
    try:
        with open(NOTIFIED_POSTS_FILE_PATH, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"오류: {NOTIFIED_POSTS_FILE_PATH} 파일 읽기 실패: {e}")
        return set()

# 알림 보낸 게시글 ID 저장 (경로 수정됨)
def save_notified_posts(notified_ids):
    """알림을 보낸 게시글 ID 목록을 파일에 저장합니다."""
    try:
        # [✅ 핵심 수정 2] 파일을 쓰기 전에 .cache 디렉토리가 있는지 확인하고 없으면 생성
        os.makedirs(CACHE_DIR, exist_ok=True) 
        
        with open(NOTIFIED_POSTS_FILE_PATH, 'w', encoding='utf-8') as f:
            for post_id in notified_ids:
                f.write(f"{post_id}\n")
    except Exception as e:
        print(f"오류: {NOTIFIED_POSTS_FILE_PATH} 파일 쓰기 실패: {e}")

# 최신 게시글 긁어오기
def fetch_recent_posts(gallery_url, pages_to_scan):
    """지정된 갤러리의 여러 페이지에서 게시글 목록을 가져옵니다."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    unique_posts = {} 
    print(f"{pages_to_scan}개의 페이지를 스캔합니다: {gallery_url}")

    for page in range(1, pages_to_scan + 1):
        page_url = f"{gallery_url}&page={page}"
        print(f"  - {page}페이지 확인 중...")
        
        try:
            response = requests.get(page_url, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.select('td.gall_tit a')
            if not posts:
                print(f"  - {page}페이지에서 게시글을 찾을 수 없습니다.")
                continue

            for post in posts:
                title = post.text.strip()
                link = post.get('href', '')
                
                if not link.startswith('/board/view/') or 'no=' not in link:
                    continue
                
                try:
                    post_id = link.split('no=')[1].split('&')[0]
                except (IndexError, AttributeError):
                    continue 
                
                if post_id not in unique_posts:
                    full_link = "https://gall.dcinside.com" + link
                    unique_posts[post_id] = (title, full_link)
                    
        except requests.exceptions.RequestException as e:
            print(f"오류: {page}페이지 접근 실패: {e}")
            continue
        except Exception as e:
            print(f"오류: {page}페이지 파싱 실패: {e}")
            continue
        
        time.sleep(0.1)

    return list(unique_posts.items())

# 메인 로직
def main():
    print("--- DC-checker 시작 ---")
    
    # 1. 이전에 알림 보낸 목록 로드
    notified_ids = load_notified_posts()
    print(f"이전에 알림 보낸 게시글 수: {len(notified_ids)} (파일: {NOTIFIED_POSTS_FILE_PATH})")
    
    # 2. 갤러리에서 최신 게시글 가져오기
    recent_posts = fetch_recent_posts(TARGET_GALLERY_URL, PAGES_TO_SCAN)
    if not recent_posts:
        print("새 글을 찾지 못했습니다 (게시글 스캔 실패).")
        print("--- DC-checker 종료 ---")
        return

    new_posts_found_count = 0
    
    # 3. [수정됨] 최신 글 목록을 순회하며 '새 글'마다 1개씩 알림 전송
    # (recent_posts는 최신순이므로, 역순(reversed)으로 돌려야 오래된 글부터 알림이 감)
    for post_id, (title, link) in reversed(recent_posts):
        
        # '새 글' (알림 목록에 없는 글)인지 확인
        if post_id not in notified_ids:
            print(f"발견! -> ID: {post_id}, 제목: {title}")
            
            # [수정됨] 메시지를 1개씩 생성
            message = f"[{title}]({link})"
            
            # [수정됨] 1개씩 알림 전송
            success = send_telegram_notification(message)
            
            # [수정됨] 알림 전송에 성공한 경우에만, 목록에 추가하고 즉시 파일에 저장
            if success:
                new_posts_found_count += 1
                notified_ids.add(post_id)
                save_notified_posts(notified_ids) # (중요) 성공할 때마다 즉시 저장
            else:
                print(f"알림 실패: ID {post_id}는 다음 실행 시 재시도됩니다.")

    if new_posts_found_count == 0:
        print("새 글을 찾지 못했습니다.")

    print(f"총 {new_posts_found_count}개의 새 알림을 전송했습니다.")
    print("--- DC-checker 종료 ---")

if __name__ == "__main__":
    main()

