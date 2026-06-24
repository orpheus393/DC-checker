// /api/boxoffice  —  박스오피스(상영 중 인기 영화) 차트 (서버리스 함수)
//
// 환경변수 TMDB_API_KEY 가 필요해요 (TMDB = The Movie Database, 무료).
// 키가 없으면 503을 반환하고, 화면은 자동으로 샘플 데이터로 폴백합니다.

export default async function handler(req, res) {
  const KEY = process.env.TMDB_API_KEY;
  if (!KEY) {
    return res.status(503).json({ error: "TMDB_API_KEY 미설정" });
  }

  const url =
    "https://api.themoviedb.org/3/movie/now_playing" +
    "?language=ko-KR&region=KR&page=1&api_key=" + KEY;

  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("TMDB API " + r.status);
    const data = await r.json();

    const items = (data.results || []).slice(0, 10).map((m) => ({
      title: m.title,
      sub: `평점 ${m.vote_average?.toFixed(1) ?? "-"} · ${m.release_date || ""}`,
      emoji: "🎬",
      change: 0,
    }));

    res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=7200");
    return res.status(200).json({
      title: "박스오피스 (상영 중 인기작)",
      meta: "실시간 · TMDB",
      items,
    });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
