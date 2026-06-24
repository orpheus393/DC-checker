// /api/youtube  —  유튜브 뮤직 인기 차트 (서버리스 함수)
//
// Vercel/Cloudflare 등 서버 환경에서 실행됩니다.
// 환경변수 YOUTUBE_API_KEY 가 필요해요 (README 참고).
// 키가 없으면 503을 반환하고, 화면은 자동으로 샘플 데이터로 폴백합니다.

export default async function handler(req, res) {
  const KEY = process.env.YOUTUBE_API_KEY;
  if (!KEY) {
    return res.status(503).json({ error: "YOUTUBE_API_KEY 미설정" });
  }

  const url =
    "https://www.googleapis.com/youtube/v3/videos" +
    "?part=snippet,statistics&chart=mostPopular" +
    "&videoCategoryId=10&regionCode=KR&maxResults=10&key=" + KEY;

  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("YouTube API " + r.status);
    const data = await r.json();

    const items = (data.items || []).map((v) => {
      const views = Number(v.statistics?.viewCount || 0);
      return {
        title: v.snippet.title,
        sub: `${v.snippet.channelTitle} · 조회수 ${views.toLocaleString("ko-KR")}`,
        emoji: "▶️",
        change: 0, // 전일 대비 변동은 별도 저장 필요 (다음 단계)
      };
    });

    res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=1800");
    return res.status(200).json({
      title: "유튜브 뮤직 인기",
      meta: "실시간 · 인기 음악 동영상",
      items,
    });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
