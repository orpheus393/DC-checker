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

이 사이트는 빌드가 필요 없는 정적 사이트라 어디든 쉽게 올라갑니다.

### 방법 A — Vercel (추천, 가장 간단)
1. https://vercel.com 가입 (GitHub 계정으로 로그인)
2. **Add New → Project → 이 저장소 선택**
3. Root Directory를 `web` 으로 지정 → **Deploy**
4. 끝. `https://chart-world.vercel.app` 같은 주소가 생깁니다.

### 방법 B — GitHub Pages
1. 저장소 **Settings → Pages**
2. Source: `Deploy from a branch`, 브랜치 선택, 폴더는 `/web`
3. 저장하면 `https://<아이디>.github.io/<저장소>/` 로 공개됩니다.

push할 때마다 자동으로 다시 배포돼요.

---

## 3. 실제 데이터 연동 (다음 단계)

`data.js`의 `CHARTS` 객체만 실제 데이터로 채우면 됩니다. 차트별 추천 데이터 소스:

| 차트 | 데이터 소스 | API 키 | 비고 |
|------|------------|--------|------|
| 🎬 박스오피스 | **TMDB API** (`/movie/now_playing`) | 무료 | 한국: 영화진흥위원회(KOBIS) 오픈API도 가능 |
| ▶️ 유튜브 뮤직 | **YouTube Data API v3** (`mostPopular`, `videoCategoryId=10`) | 무료(쿼터) | Google Cloud Console에서 키 발급 |
| 🎵 빌보드 | 공식 API 없음 | — | 공개 데이터셋/RSS 또는 직접 집계 필요 |

> ⚠️ 빌보드처럼 공식 API가 없는 차트를 크롤링할 때는 해당 사이트의 이용약관과 `robots.txt`를 반드시 확인하세요.

### 연동 시 권장 구조
지금은 정적 사이트라 API 키를 브라우저에 노출하면 안 됩니다.
실제 연동 단계에서는 **작은 백엔드(서버리스 함수)** 를 두어
서버에서 API를 호출하고 결과만 화면에 내려주는 방식을 추천합니다.
(Vercel Functions, Cloudflare Workers 등 무료로 가능)

---

## 파일 구조
```
web/
├── index.html   # 화면 + 디자인 + 탭 전환 로직
├── data.js      # 차트 데이터 (지금은 샘플 → 실제 API로 교체)
└── README.md    # 이 문서
```
