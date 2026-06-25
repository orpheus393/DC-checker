// /api/movies — Apple 인기 영화 (키 불필요). 상세 정보(줄거리 등) 포함.

export default async function handler(req, res) {
  const url = "https://itunes.apple.com/kr/rss/topmovies/limit=10/json";
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("Apple " + r.status);
    const data = await r.json();
    const items = (data.feed?.entry || []).map((e) => {
      const imgs = e["im:image"] || [];
      return {
        title: e["im:name"]?.label || "",
        sub: e["im:artist"]?.label || "영화",
        image: imgs[imgs.length - 1]?.label,
        link: e.link?.attributes?.href,
        linkLabel: "Apple에서 보기",
        desc: e.summary?.label || "",
        emoji: "🎬",
        change: 0,
        meta: [
          e.category?.attributes?.label && { k: "장르", v: e.category.attributes.label },
          e["im:releaseDate"]?.attributes?.label && { k: "개봉", v: e["im:releaseDate"].attributes.label },
          e["im:price"]?.label && { k: "가격", v: e["im:price"].label },
        ].filter(Boolean),
      };
    });
    res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=7200");
    return res.status(200).json({ title: "인기 영화", meta: "실시간 · Apple", items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
