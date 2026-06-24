// ───────────────────────────────────────────────────────────
//  차트 샘플 데이터 (디자인 확인용)
//
//  실제 실시간 데이터로 교체하는 방법은 README.md 참고.
//  change 값 규칙:  양수 = 상승(▲), 음수 = 하락(▼), 0 = 변동없음(—), 'new' = 신규진입
// ───────────────────────────────────────────────────────────

const CHARTS = {
  billboard: {
    title: "빌보드 HOT 100",
    meta: "샘플 · 주간 차트",
    items: [
      { title: "Golden Hour",      sub: "Aurora Vale",            emoji: "🌅", change: 2 },
      { title: "Neon Tokyo",       sub: "The Midnight Run",       emoji: "🏙️", change: -1 },
      { title: "Paper Hearts",     sub: "Lila Moon",              emoji: "💌", change: 0 },
      { title: "Gravity",          sub: "Echo & The Static",      emoji: "🪐", change: 5 },
      { title: "Saltwater",        sub: "Coastline",              emoji: "🌊", change: "new" },
      { title: "Velvet Sky",       sub: "Nova Lane",              emoji: "🌌", change: -2 },
      { title: "Run It Back",      sub: "DJ Halcyon",             emoji: "🔁", change: 1 },
      { title: "Wildfire",         sub: "Ember Rose",             emoji: "🔥", change: -3 },
      { title: "Slow Motion",      sub: "Caspian",                emoji: "🎞️", change: 4 },
      { title: "Daydream",         sub: "Marigold",               emoji: "☁️", change: 0 },
    ],
  },

  boxoffice: {
    title: "박스오피스 TOP 10",
    meta: "샘플 · 주말 흥행 순위",
    items: [
      { title: "별의 계승자",        sub: "SF · 누적 312만",        emoji: "🚀", change: 0 },
      { title: "한겨울의 약속",      sub: "드라마 · 누적 198만",     emoji: "❄️", change: 1 },
      { title: "추격: 마지막 밤",    sub: "범죄 · 누적 154만",       emoji: "🌃", change: -1 },
      { title: "고양이 탐정단",      sub: "애니 · 누적 121만",       emoji: "🐱", change: "new" },
      { title: "붉은 사막",          sub: "액션 · 누적 99만",        emoji: "🏜️", change: 2 },
      { title: "오케스트라",         sub: "음악 · 누적 76만",        emoji: "🎻", change: -2 },
      { title: "마지막 등대지기",    sub: "드라마 · 누적 64만",      emoji: "🗼", change: 1 },
      { title: "유령 호텔",          sub: "공포 · 누적 51만",        emoji: "👻", change: -3 },
      { title: "웃음의 기술",        sub: "코미디 · 누적 40만",      emoji: "🎭", change: 0 },
      { title: "심해의 비밀",        sub: "다큐 · 누적 22만",        emoji: "🐋", change: "new" },
    ],
  },

  youtube: {
    title: "유튜브 뮤직 인기",
    meta: "샘플 · 실시간 조회수 급상승",
    items: [
      { title: "EITHER WAY",        sub: "STARLIT · 조회수 4,210만", emoji: "✨", change: 3 },
      { title: "한여름 밤",          sub: "오월의 정원 · 3,880만",    emoji: "🌙", change: 0 },
      { title: "REWIND",            sub: "PLUTO · 3,140만",          emoji: "⏪", change: -1 },
      { title: "첫차",              sub: "노을빛 · 2,760만",         emoji: "🚌", change: 6 },
      { title: "Cherry Cola",       sub: "Minty · 2,500만",          emoji: "🍒", change: "new" },
      { title: "비가 오면",          sub: "우산 없는 날 · 2,210만",   emoji: "☔", change: -2 },
      { title: "BOOM",              sub: "VOLT · 1,990만",           emoji: "💥", change: 1 },
      { title: "산책",              sub: "고요 · 1,640만",           emoji: "🚶", change: 2 },
      { title: "Sugar Rush",        sub: "Bonbon · 1,420만",         emoji: "🍬", change: -4 },
      { title: "마지막 인사",        sub: "겨울편지 · 1,180만",       emoji: "👋", change: 0 },
    ],
  },
};
