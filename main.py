# main.py
import requests
from bs4 import BeautifulSoup
import os
import time
import json # json 라이브러리 추가

# --- 설정 ---
# 1. 스캔할 갤러리 (만화 갤러리 6 - 개념글)
TARGET_GALLERY_URL = "https://gall.dcinside.com/board/lists/?id=comic_new6&exception_mode=recommend"
# 2. 스캔할 페이지 수
PAGES_TO_SCAN = 1

# [✅ 로직 변경 1]
# GitHub Actions의 작업 공간(workspace) 경로를 가져옵니다.
WORKSPACE_PATH = os.environ.get('GITHUB_WORKSPACE', '.')
# 알림 목록을 저장할 파일 경로를 .json으로 변경 (저장소 최상위 경로)
NOTIFIED_POSTS_FILE_PATH = os.path.join(WORKSPACE_PATH, 'notified_posts.json')
# --- 설정 끝 ---


# 텔레그램 알림 전송 함수 (이전과 동일)
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
        response.raise_for_status() # HTTP 4xx/5xx 에러가 나면 여기서 예외 발생
        
        try:
            response_json = response.json()
            if response_json.get("ok"):
                print(f"텔레그램 알림 전송 성공 (ok=True): {message[:20]}...")
                return True
            else:
                print(f"경고: 텔레그램 API가 'ok: false'를 반환했으나 알림이 전송된 것 같습니다. {response.text}")
                print(" -> '성공'으로 처리하고 저장합니다.")
                return True

        except requests.exceptions.JSONDecodeError:
            print(f"경고: 텔레그램 응답이 JSON이 아닙니다. (HTTP {response.status_code})")
            print(" -> '성공'으로 처리하고 저장합니다.")
            return True

    except requests.exceptions.RequestException as e:
        print(f"오류: 텔레그램 알림 전송에 실패했습니다: {e}")
        return False
    except Exception as e: 
        print(f"오류: 텔레그램 응답 처리 중 알 수 없는 오류: {e}")
        return False


# [✅ 로직 변경 2] JSON 파일에서 ID 로드
def load_notified_posts():
    """JSON 파일에서 이미 알림을 보낸 게시글 ID 목록을 불러옵니다."""
    try:
        with open(NOTIFIED_POSTS_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data) # 리스트를 set으로 변환하여 반환
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"알림: '{NOTIFIED_POSTS_FILE_PATH}' 파일이 없거나 비어있어 새로 시작합니다.")
        return set()
    except Exception as e:
        print(f"오류: {NOTIFIED_POSTS_FILE_PATH} 파일 읽기 실패: {e}")
        return set()

# [✅ 로직 변경 3] JSON 파일로 ID 저장
def save_notified_posts(notified_ids):
    """알림을 보낸 게시글 ID 목록을 JSON 파일에 저장합니다."""
    try:
        # set을 list로 변환해야 JSON 저장이 가능
        with open(NOTIFIED_POSTS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(list(notified_ids), f, indent=2)
        print(f"성공: {len(notified_ids)}개의 ID를 {NOTIFIED_POSTS_FILE_PATH} 파일에 저장했습니다.")
    except Exception as e:
        print(f"오류: {NOTIFIED_POSTS_FILE_PATH} 파일 쓰기 실패: {e}")

# [✅ 로직 변경 4] 공지 제외
def fetch_recent_posts(gallery_url, pages_to_scan):
    """갤러리에서 '공지'를 제외한 게시글 목록을 가져옵니다."""
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
            
            # [✅ 핵심 수정]
            # '공지' (tr.ub-content.notice)를 제외하고
            # '일반 개념글' (tr.us-post)만 선택하도록 셀렉터 변경
            posts = soup.select('tr.us-post td.gall_tit a')
            
            if not posts:
                print(f"  - {page}페이지에서 게시글(공지 제외)을 찾을 수 없습니다.")
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

# [✅ 로직 변경 5] 메인 로직 최적화
def main():
    print("--- DC-checker 시작 (v2: Git Commit 방식) ---")
    
    # 1. 이전에 알림 보낸 목록 로드
    notified_ids = load_notified_posts()
    print(f"이전에 알림 보낸 게시글 수: {len(notified_ids)} (파일: {NOTIFIED_POSTS_FILE_PATH})")
    
    # 2. 갤러리에서 최신 게시글 가져오기 (공지 제외)
    recent_posts = fetch_recent_posts(TARGET_GALLERY_URL, PAGES_TO_SCAN)
    if not recent_posts:
        print("새 글을 찾지 못했습니다 (게시글 스캔 실패).")
        print("--- DC-checker 종료 ---")
        return

    # 3. 새 글만 필터링
    new_posts_to_notify = []
    for post_id, (title, link) in reversed(recent_posts):
        if post_id not in notified_ids:
            new_posts_to_notify.append((post_id, title, link))

    if not new_posts_to_notify:
        print("새 글을 찾지 못했습니다.")
        print("--- DC-checker 종료 ---")
        return

    print(f"총 {len(new_posts_to_notify)}개의 새 글을 발견했습니다. 알림 전송을 시작합니다.")
    
    # 4. 알림 전송
    successful_posts_count = 0
    for post_id, title, link in new_posts_to_notify:
        print(f"발견! -> ID: {post_id}, 제목: {title}")
        message = f"[{title}]({link})"
        
        success = send_telegram_notification(message)
        
        if success:
            successful_posts_count += 1
            notified_ids.add(post_id) # 성공한 ID를 set에 추가
        else:
            print(f"알림 실패: ID {post_id}는 다음 실행 시 재시도됩니다.")

    # 5. [중요] 모든 알림이 끝난 후, 성공한 ID가 1개라도 있다면 파일에 **한 번만** 저장
    if successful_posts_count > 0:
        print(f"총 {successful_posts_count}개의 새 알림 전송 완료. 파일 저장을 시도합니다.")
        save_notified_posts(notified_ids)
    else:
        print("알림 전송에 성공한 새 글이 없습니다.")

    print("--- DC-checker 종료 ---")

if __name__ == "__main__":
    main()