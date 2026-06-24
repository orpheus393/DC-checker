// /api/music — Apple Music 인기곡 (키 불필요)
// 브라우저가 CORS로 직접 호출을 막을 때를 대비한 서버 측 프록시.

export default async function handler(req, res) {
  const url = "https://rss.marketingtools.apple.com/api/v2/kr/music/most-played/25/songs.json";
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("Apple " + r.status);
    const data = await r.json();
    const items = (data.feed?.results || []).slice(0, 10).map((s) => ({
      title: s.name,
      sub: s.artistName,
      emoji: "🎵",
      change: 0,
    }));
    res.setHeader("Cache-Control", "s-maxage=1800, stale-while-revalidate=3600");
    return res.status(200).json({ title: "글로벌 인기 음악", meta: "실시간 · Apple Music", items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
