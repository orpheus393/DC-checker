// ───────────────────────────────────────────────────────────
//  차트 폴백(샘플) 데이터
//
//  실시간 데이터를 못 불러올 때만(네트워크/CORS 차단 등) 이 값이 표시됩니다.
//  평소에는 index.html이 실시간 소스에서 데이터를 가져와요.
//  change 규칙:  양수=상승(▲)  음수=하락(▼)  0=변동없음(—)  'new'=신규
// ───────────────────────────────────────────────────────────

const CHARTS = {
  music: {
    title: "글로벌 인기 음악",
    meta: "샘플 · 실시간 연결 실패 시 표시",
    items: [
      { title: "Golden Hour",  sub: "Aurora Vale",       emoji: "🎵", change: 2 },
      { title: "Neon Tokyo",   sub: "The Midnight Run",   emoji: "🎵", change: -1 },
      { title: "Paper Hearts", sub: "Lila Moon",          emoji: "🎵", change: 0 },
      { title: "Gravity",      sub: "Echo & The Static",  emoji: "🎵", change: 5 },
      { title: "Saltwater",    sub: "Coastline",          emoji: "🎵", change: "new" },
    ],
  },

  movies: {
    title: "인기 영화",
    meta: "샘플 · 실시간 연결 실패 시 표시",
    items: [
      { title: "별의 계승자",     sub: "SF",        emoji: "🎬", change: 0 },
      { title: "한겨울의 약속",   sub: "드라마",    emoji: "🎬", change: 1 },
      { title: "추격: 마지막 밤", sub: "범죄",      emoji: "🎬", change: -1 },
      { title: "고양이 탐정단",   sub: "애니메이션", emoji: "🎬", change: "new" },
      { title: "붉은 사막",       sub: "액션",      emoji: "🎬", change: 2 },
    ],
  },

  youtube: {
    title: "유튜브 뮤직 인기",
    meta: "샘플 · 실시간엔 YouTube API 키 필요",
    items: [
      { title: "EITHER WAY", sub: "STARLIT",        emoji: "▶️", change: 3 },
      { title: "한여름 밤",   sub: "오월의 정원",     emoji: "▶️", change: 0 },
      { title: "REWIND",     sub: "PLUTO",          emoji: "▶️", change: -1 },
      { title: "첫차",       sub: "노을빛",          emoji: "▶️", change: 6 },
      { title: "Cherry Cola", sub: "Minty",         emoji: "▶️", change: "new" },
    ],
  },

  billboard: {
    title: "빌보드 HOT 100",
    meta: "샘플 · 공식 API가 없어 직접 집계 필요",
    items: [
      { title: "Golden Hour", sub: "Aurora Vale",       emoji: "🏆", change: 2 },
      { title: "Wildfire",    sub: "Ember Rose",         emoji: "🏆", change: -3 },
      { title: "Slow Motion", sub: "Caspian",            emoji: "🏆", change: 4 },
      { title: "Daydream",    sub: "Marigold",           emoji: "🏆", change: 0 },
      { title: "Velvet Sky",  sub: "Nova Lane",          emoji: "🏆", change: -2 },
    ],
  },
};
