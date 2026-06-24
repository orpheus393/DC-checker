// /api/movies — Apple 인기 영화 (키 불필요)
// 브라우저가 CORS로 직접 호출을 막을 때를 대비한 서버 측 프록시.

export default async function handler(req, res) {
  const url = "https://itunes.apple.com/kr/rss/topmovies/limit=10/json";
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("Apple " + r.status);
    const data = await r.json();
    const items = (data.feed?.entry || []).map((e) => ({
      title: e["im:name"]?.label || "",
      sub: e["im:artist"]?.label || "영화",
      emoji: "🎬",
      change: 0,
    }));
    res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=7200");
    return res.status(200).json({ title: "인기 영화", meta: "실시간 · Apple", items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
