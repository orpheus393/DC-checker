# CHART WORLD 🎬🎵

영화·음악·세상의 모든 차트(빌보드, 박스오피스, 유튜브 뮤직 등)를 한눈에 보여주는 웹사이트입니다.

> 현재는 **디자인 확인용 프로토타입**이에요. 화면에 보이는 순위는 `data.js`의 샘플 데이터입니다.
> 실제 실시간 차트로 바꾸는 방법은 아래 "실제 데이터 연동"을 참고하세요.

---

## 1. 지금 바로 화면 보기 (로컬)

별도 설치 없이 `web/index.html`을 브라우저로 열기만 하면 됩니다.
(또는 폴더에서 아래 명령으로 간단한 서버 실행)

```bash
cd web
python -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```

---

## 2. 클라우드 배포 (무료)

배포 설정 파일은 이미 저장소에 들어 있어요. 둘 중 하나를 고르세요.

### 방법 A — Vercel (★ 실시간 데이터까지 쓰려면 이걸로)
서버리스 함수(`/api`)가 동작해서 **실시간 차트**를 쓸 수 있습니다.
1. https://vercel.com 가입 (GitHub 계정으로 로그인)
2. **Add New → Project → 이 저장소(`DC-checker`) 선택**
3. **Root Directory → `web`** 으로 지정
4. (실시간 데이터용) **Environment Variables** 에 API 키 입력 — 아래 3번 참고
5. **Deploy** → `https://....vercel.app` 주소 생성. 이후 push마다 자동 재배포.

### 방법 B — GitHub Pages (정적, 샘플 데이터만)
워크플로우(`.github/workflows/pages.yml`)가 이미 있어요. **최초 1회만**:
1. 저장소 **Settings → Pages → Source 를 `GitHub Actions`** 로 설정
2. `main` 브랜치에 머지되면 자동 배포 → `https://<아이디>.github.io/DC-checker/`

> GitHub Pages는 서버가 없어 `/api` 함수가 안 돌아갑니다 → 화면은 자동으로 **샘플 데이터**로 표시돼요.
> 실시간 데이터가 필요하면 **방법 A(Vercel)** 를 쓰세요.

---

## 3. 실시간 데이터 (대부분 키 불필요!)

| 차트 | 데이터 소스 | API 키 | 상태 |
|------|------------|--------|------|
| 🎵 인기 음악 | Apple Music 공개 RSS | **불필요** | 바로 실시간 |
| 🎬 인기 영화 | Apple 공개 RSS | **불필요** | 바로 실시간 |
| ▶️ 유튜브 뮤직 | YouTube Data API v3 | 필요(무료) | 키 넣으면 실시간 |
| 🏆 빌보드 | 공식 API 없음 | — | 샘플 유지 |

동작 순서: 화면이 ① 브라우저에서 직접 호출 → ② (실패 시) 서버리스 함수 → ③ (둘 다 실패 시) 샘플 순으로 시도합니다.
- 로컬에서 `index.html`을 열면 브라우저 보안(CORS)으로 직접 호출이 막힐 수 있어요 → 그땐 샘플로 보입니다.
- **클라우드(Vercel)에 배포하면** 서버리스 함수가 대신 가져와 음악·영화는 **항상 실시간**으로 표시됩니다.

### 유튜브까지 실시간으로 (선택)
Vercel 프로젝트 → **Settings → Environment Variables** 에 `YOUTUBE_API_KEY` 추가 → Redeploy.
키는 Google Cloud Console → API 및 서비스 → 사용자 인증 정보에서 무료 발급.

> ⚠️ API 키는 브라우저 코드(`index.html`/`data.js`)에 직접 넣지 마세요.
> 서버리스 함수(`/api/youtube.js`)가 서버에서만 키를 읽습니다.

---

## 파일 구조
```
web/
├── index.html        # 화면 + 디자인 + 탭 전환 (실시간 fetch → 실패 시 샘플 폴백)
├── data.js           # 샘플/폴백 차트 데이터
└── README.md         # 이 문서

(저장소 루트)
├── vercel.json       # Vercel 배포 설정 (outputDirectory=web)
└── api/
    ├── music.js      # 인기 음악 실시간 (Apple, 키 불필요)
    ├── movies.js     # 인기 영화 실시간 (Apple, 키 불필요)
    └── youtube.js    # 유튜브 뮤직 실시간 (YOUTUBE_API_KEY 필요)
```
