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

## 3. 실시간 데이터 연동

서버리스 함수가 이미 만들어져 있어요 (`web/api/youtube.js`, `web/api/boxoffice.js`).
**API 키만 발급받아 Vercel 환경변수에 넣으면** 화면 배지가 `샘플` → `실시간` 으로 바뀝니다.
(키가 없으면 자동으로 샘플 데이터로 폴백하므로 망가지지 않아요.)

| 차트 | 데이터 소스 | 환경변수 이름 | 키 발급처 |
|------|------------|--------------|-----------|
| ▶️ 유튜브 뮤직 | YouTube Data API v3 | `YOUTUBE_API_KEY` | Google Cloud Console → API 및 서비스 → 사용자 인증 정보 |
| 🎬 박스오피스 | TMDB (The Movie Database) | `TMDB_API_KEY` | https://www.themoviedb.org → 설정 → API (무료) |
| 🎵 빌보드 | 공식 API 없음 | — | 샘플 유지 (공개 데이터셋/직접 집계 필요) |

### 키 넣는 곳
Vercel 프로젝트 → **Settings → Environment Variables** 에서 위 이름으로 추가 → **Redeploy**.

> ⚠️ API 키는 절대 `index.html`/`data.js` 같은 브라우저 코드에 직접 넣지 마세요.
> 서버리스 함수(`/api`)가 서버에서만 키를 읽도록 설계돼 있습니다.
> 빌보드처럼 공식 API가 없는 차트를 크롤링할 때는 해당 사이트 이용약관과 `robots.txt`를 확인하세요.

---

## 파일 구조
```
web/
├── index.html        # 화면 + 디자인 + 탭 전환 (실시간 fetch → 실패 시 샘플 폴백)
├── data.js           # 샘플/폴백 차트 데이터
├── vercel.json       # Vercel 배포 설정
├── api/
│   ├── youtube.js    # 유튜브 뮤직 실시간 (YOUTUBE_API_KEY 필요)
│   └── boxoffice.js  # 박스오피스 실시간 (TMDB_API_KEY 필요)
└── README.md         # 이 문서
```
