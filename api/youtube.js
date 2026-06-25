// /api/youtube — 유튜브 뮤직 인기 차트 (서버리스 함수)
//
// 1순위: 공식 YouTube Data API (환경변수 YOUTUBE_API_KEY 가 있을 때) — 가장 정확/안정
// 2순위: 키가 없으면 Invidious 공개 미러에서 '음악 인기'를 키 없이 시도 (불안정할 수 있음)
// 둘 다 실패하면 502 → 화면이 자동으로 샘플 데이터로 폴백합니다.

const RESULT = (items, src) => ({
  title: "유튜브 뮤직 인기",
  meta: src === "mirror" ? "실시간 · 공개 미러" : "실시간 · 인기 음악 동영상",
  items,
});

// ── 1순위: 공식 API ──────────────────────────────
async function viaOfficial(key) {
  const url =
    "https://www.googleapis.com/youtube/v3/videos" +
    "?part=snippet,statistics&chart=mostPopular" +
    "&videoCategoryId=10&regionCode=KR&maxResults=10&key=" + key;
  const r = await fetch(url);
  if (!r.ok) throw new Error("YouTube API " + r.status);
  const data = await r.json();
  return (data.items || []).map((v) => {
    const sn = v.snippet, st = v.statistics || {};
    return {
      title: sn.title,
      sub: sn.channelTitle,
      image: sn.thumbnails?.medium?.url || sn.thumbnails?.default?.url,
      link: "https://www.youtube.com/watch?v=" + v.id,
      linkLabel: "유튜브에서 보기",
      desc: (sn.description || "").slice(0, 300),
      emoji: "▶️",
      change: 0,
      meta: [
        st.viewCount && { k: "조회수", v: Number(st.viewCount).toLocaleString("ko-KR") + "회" },
        st.likeCount && { k: "좋아요", v: Number(st.likeCount).toLocaleString("ko-KR") },
        sn.publishedAt && { k: "게시일", v: sn.publishedAt.slice(0, 10) },
      ].filter(Boolean),
    };
  });
}

// ── 2순위: 키 없는 Invidious 미러 ────────────────
// 공개 인스턴스는 수시로 변동/차단됩니다. 순서대로 시도.
const MIRRORS = [
  "https://invidious.nerdvpn.de",
  "https://inv.nadeko.net",
  "https://yewtu.be",
  "https://invidious.fdn.fr",
];

async function viaMirror() {
  for (const base of MIRRORS) {
    try {
      const r = await fetch(`${base}/api/v1/trending?type=Music&region=KR`, {
        headers: { "User-Agent": "Mozilla/5.0" },
        signal: AbortSignal.timeout(6000),
      });
      if (!r.ok) continue;
      const arr = await r.json();
      if (!Array.isArray(arr) || !arr.length) continue;
      return arr.slice(0, 10).map((v) => ({
        title: v.title,
        sub: v.author || "",
        image: (v.videoThumbnails || []).find((t) => t.quality === "medium")?.url
          || (v.videoThumbnails || [])[0]?.url,
        link: "https://www.youtube.com/watch?v=" + v.videoId,
        linkLabel: "유튜브에서 보기",
        desc: (v.description || "").slice(0, 300),
        emoji: "▶️",
        change: 0,
        meta: [
          v.viewCount && { k: "조회수", v: Number(v.viewCount).toLocaleString("ko-KR") + "회" },
        ].filter(Boolean),
      }));
    } catch (e) { /* 다음 미러 시도 */ }
  }
  throw new Error("모든 미러 실패");
}

export default async function handler(req, res) {
  const key = process.env.YOUTUBE_API_KEY;
  try {
    const items = key ? await viaOfficial(key) : await viaMirror();
    res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=1800");
    return res.status(200).json(RESULT(items, key ? "official" : "mirror"));
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
