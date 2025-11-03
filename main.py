import requests
import time
import os
from bs4 import BeautifulSoup

# --- 설정 ---

# 1. 모니터링할 갤러리 URL (예: 만화 갤러리)
TARGET_GALLERY_URL = "https://gall.dcinside.com/board/lists/?id=cartoon"

# 2. 찾고 싶은 키워드 목록 (이 중 하나라도 제목에 포함되면 알림)
TARGET_KEYWORDS = ["특정제목1", "원하는만화"]

# 3. (중요) 게시글 제목을 포함하는 요소의 CSS 선택자
#    이 값은 갤러리 종류(일반/마이너)나 PC/모바일 버전에 따라 다를 수 있습니다.
#    작동하지 않으면 README.md의 'CSS 선택자 찾기' 부분을 참고하세요.
#    예: 'a.gallery-list-item', 'td.gall_tit a' 등
CSS_SELECTOR_FOR_POSTS = "td.gall_tit a" # 일반 갤러리 목록의 제목 선택자 예시

# 4. 이미 알림을 보낸 게시글을 기록할 파일
NOTIFIED_POSTS_FILE = "notified_posts.txt"

# 5. (선택) Discord 웹훅 URL (GitHub Actions Secrets에서 가져옴)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- /설정 ---


def fetch_recent_posts():
    """갤러리에서 최신 게시글 목록을 가져옵니다."""
    print(f"갤러리 확인 중: {TARGET_GALLERY_URL}")
    
    # DC인사이드는 User-Agent 헤더가 없으면 차단하는 경우가 많습니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(TARGET_GALLERY_URL, headers=headers)
        response.raise_for_status() # 오류가 있으면 예외 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # CSS 선택자를 사용해 게시글 제목 요소들을 모두 찾습니다.
        post_elements = soup.select(CSS_SELECTOR_FOR_POSTS)
        
        if not post_elements:
            print(f"경고: CSS 선택자 '{CSS_SELECTOR_FOR_POSTS}'로 게시글을 찾을 수 없습니다.")
            print("README의 'CSS 선택자 찾기'를 참고하여 선택자를 수정하세요.")
            return []

        found_posts = []
        for el in post_elements:
            title = el.get_text(strip=True)
            # href 속성에서 실제 게시글 URL을 추출합니다.
            # 상대 경로일 수 있으므로 (예: /board/view/...) 완전한 URL로 만들어줍니다.
            url = el.get('href', '')
            if not url.startswith('http'):
                url = "https://gall.dcinside.com" + url
                
            # 게시글 번호(또는 고유 ID)를 URL에서 추출하려 시도
            # 예: .../board/view/?id=cartoon&no=12345
            post_id = url.split('no=')[-1].split('&')[0]
            
            if post_id:
                found_posts.append({'id': post_id, 'title': title, 'url': url})
        
        return found_posts

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져오는 데 실패했습니다 - {e}")
        return []

def load_notified_posts():
    """이미 알림을 보낸 게시글 ID 목록을 파일에서 불러옵니다."""
    if not os.path.exists(NOTIFIED_POSTS_FILE):
        return set()
    
    with open(NOTIFIED_POSTS_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def save_notified_post(post_id):
    """알림을 보낸 게시글 ID를 파일에 추가합니다."""
    with open(NOTIFIED_POSTS_FILE, 'a', encoding='utf-8') as f:
        f.write(post_id + '\n')

def send_discord_notification(post):
    """Discord 웹훅으로 알림을 보냅니다."""
    if not DISCORD_WEBHOOK_URL:
        print("알림: Discord 웹훅 URL이 설정되지 않았습니다. 콘솔에만 출력합니다.")
        return

    message = f"🚨 새 글 발견! 🚨\n\n**{post['title']}**\n{post['url']}"
    
    payload = {
        "content": message
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"알림: Discord로 알림을 성공적으로 보냈습니다. (ID: {post['id']})")
    except requests.exceptions.RequestException as e:
        print(f"오류: Discord 알림 전송에 실패했습니다 - {e}")

def main():
    print("--- DC-checker 시작 ---")
    
    # 1. 갤러리에서 최신 글 가져오기
    recent_posts = fetch_recent_posts()
    if not recent_posts:
        print("게시글을 가져오지 못했거나 오류가 발생했습니다.")
        print("--- DC-checker 종료 ---")
        return

    # 2. 이미 알림 보낸 글 목록 가져오기
    notified_ids = load_notified_posts()
    
    # 3. 새 글 확인
    new_posts_found = []
    
    for post in recent_posts:
        # 키워드가 포함되어 있고, 아직 알림 보낸 적 없는 글인지 확인
        if post['id'] not in notified_ids:
            for keyword in TARGET_KEYWORDS:
                if keyword in post['title']:
                    new_posts_found.append(post)
                    break # 이 게시글은 이미 찾았으므로 다음 게시글로 넘어감

    # 4. 알림 보내기
    if not new_posts_found:
        print("새 글을 찾지 못했습니다.")
    else:
        for post in new_posts_found:
            print(f"발견! -> ID: {post['id']}, 제목: {post['title']}")
            # 알림 보내기 (Discord 등)
            send_discord_notification(post)
            # 알림 보낸 목록에 추가
            save_notified_post(post['id'])
            # 서버에 부담을 주지 않기 위해 약간의 지연
            time.sleep(1) 

    print("--- DC-checker 종료 ---")

if __name__ == "__main__":
    main()
