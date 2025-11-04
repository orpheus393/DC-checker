DC-checker

디시인사이드 갤러리(기본: 만화 갤러리 6 개념글)에 특정 제목의 게시글이 올라오면 **텔레그램(Telegram)**으로 알림을 보내주는 파이썬 스크립트입니다.

🌟 주요 기능

지정된 DCInside 갤러리의 개념글(추천글) 목록을 크롤링합니다.

게시글 제목에 원하는 키워드가 포함되어 있는지 확인합니다.

키워드가 포함된 새 글이 발견되면 지정된 텔레그램 봇으로 알림을 보냅니다.

🚀 시작하는 법

1. 환경 설정

이 프로젝트는 Python 3가 필요합니다.

먼저, 필요한 라이브러리를 설치합니다. (의존성은 requests, beautifulsoup4 뿐입니다.)

pip install -r requirements.txt


2. 스크립트 실행

main.py 파일을 수정하여 TARGET_GALLERY_URL과 TARGET_KEYWORDS를 원하는 값으로 변경하세요.

로컬에서 테스트로 실행할 경우, 텔레그램 설정값이 없어 콘솔에만 출력된다는 메시지를 보여줄 것입니다.

python main.py


⚙️ 자동화 (GitHub Actions)

이 저장소에는 .github/workflows/main.yml 파일이 포함되어 있습니다. 이 파일은 60분마다 이 스크립트를 자동으로 실행하도록 설정되어 있습니다.

텔레그램 알림을 받으려면 GitHub 저장소에 Secrets를 등록해야 합니다.

1. (중요) 텔레그램 봇 토큰 및 채팅 ID 발급받기

A. 봇 토큰 (BOT_TOKEN) 발급받기

텔레그램 앱에서 @BotFather 를 검색하여 대화를 시작합니다.

/newbot 이라고 입력하고 전송합니다.

봇의 이름 (예: DC Checker)과 사용자 이름 (예: My_DC_checker_bot, _bot으로 끝나야 함)을 차례대로 입력합니다.

BotFather가 Use this token to access the HTTP API:라며 긴 토큰을 알려줍니다. 이 토큰을 복사해서 안전한 곳에 보관하세요. (이것이 TELEGRAM_BOT_TOKEN입니다.)

B. 채팅 ID (CHAT_ID) 발급받기

텔레그램 앱에서 @get_id_bot 또는 @myidbot 을 검색하여 대화를 시작합니다.

/start 라고 입력하고 전송합니다.

봇이 Your user ID: 123456789와 같이 숫자로 된 ID를 알려줍니다. 이 숫자를 복사하세요. (이것이 TELEGRAM_CHAT_ID입니다.)

C. (필수!) 봇과 대화 시작하기

A단계에서 만든 자신의 봇 (예: @My_DC_checker_bot)을 텔레그램에서 검색하여 대화를 시작해야 합니다.

/start 라고 한 번 입력하고 전송하세요. (이 과정을 거치지 않으면, 봇이 사용자에게 메시지를 보낼 권한이 없어 알림이 오지 않습니다.)

2. GitHub Secrets 설정하기

이 GitHub 저장소(orpheus393/DC-checker)의 [Settings] 탭으로 이동합니다.

왼쪽 메뉴에서 [Secrets and variables] > **[Actions]**를 선택합니다.

[New repository secret] 버튼을 눌러 새로운 Secret 2개를 등록합니다.

TELEGRAM_BOT_TOKEN:

A단계에서 BotFather에게 발급받은 봇 토큰을 붙여넣습니다. (예: 110201543:AAHdqTcv...)

TELEGRAM_CHAT_ID:

B단계에서 @get_id_bot에게 받은 숫자 ID를 붙여넣습니다. (예: 123456789)

⚠️ 주의사항

웹 크롤링은 대상 웹사이트의 이용 약관 및 robots.txt 파일을 준수해야 합니다. 과도한 요청으로 서버에 부담을 주지 않도록 주의하세요.
