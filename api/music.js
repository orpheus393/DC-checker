// /api/music — Apple Music 인기곡 (키 불필요). 상세 정보 포함.

export default async function handler(req, res) {
  const url = "https://rss.marketingtools.apple.com/api/v2/kr/music/most-played/25/songs.json";
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("Apple " + r.status);
    const data = await r.json();
    const items = (data.feed?.results || []).slice(0, 10).map((s) => {
      const genre = (s.genres || []).map((g) => g.genreName).filter((n) => n !== "Music")[0];
      return {
        title: s.name,
        sub: s.artistName,
        image: s.artworkUrl100,
        link: s.url,
        linkLabel: "Apple Music에서 보기",
        emoji: "🎵",
        change: 0,
        meta: [
          genre && { k: "장르", v: genre },
          s.releaseDate && { k: "발매일", v: s.releaseDate },
        ].filter(Boolean),
      };
    });
    res.setHeader("Cache-Control", "s-maxage=1800, stale-while-revalidate=3600");
    return res.status(200).json({ title: "글로벌 인기 음악", meta: "실시간 · Apple Music", items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
