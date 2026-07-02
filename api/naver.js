// /api/naver — 네이버 검색 오픈API로 "관련 소식"(뉴스·블로그) 가져오기
//
// 각 차트 항목이 왜 화제인지 맥락을 실제 기사/블로그로 보여주기 위한 함수.
// 환경변수 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 필요 (developers.naver.com 무료 발급).
// 키가 없으면 503 → 화면은 "관련 소식" 영역을 조용히 숨김.
//
// 사용: /api/naver?q=검색어

const clean = (s) =>
  String(s || "")
    .replace(/<[^>]*>/g, "")
    .replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">").replace(/&#39;/g, "'").replace(/&nbsp;/g, " ")
    .trim();

export default async function handler(req, res) {
  const id = process.env.NAVER_CLIENT_ID;
  const secret = process.env.NAVER_CLIENT_SECRET;
  if (!id || !secret) return res.status(503).json({ error: "NAVER 키 미설정" });

  const q = String(req.query?.q || "").slice(0, 100).trim();
  if (!q) return res.status(400).json({ error: "q(검색어) 필요" });

  const headers = { "X-Naver-Client-Id": id, "X-Naver-Client-Secret": secret };
  const enc = encodeURIComponent(q);

  try {
    const [newsR, blogR] = await Promise.all([
      fetch(`https://openapi.naver.com/v1/search/news.json?query=${enc}&display=4&sort=sim`, { headers }),
      fetch(`https://openapi.naver.com/v1/search/blog.json?query=${enc}&display=3&sort=sim`, { headers }),
    ]);
    const news = newsR.ok ? (await newsR.json()).items || [] : [];
    const blog = blogR.ok ? (await blogR.json()).items || [] : [];

    const items = [
      ...news.map((n) => ({
        type: "뉴스",
        title: clean(n.title),
        desc: clean(n.description),
        link: n.originallink || n.link,
        date: (n.pubDate || "").slice(0, 16),
      })),
      ...blog.map((b) => ({
        type: "블로그",
        title: clean(b.title),
        desc: clean(b.description),
        link: b.link,
        source: clean(b.bloggername),
        date: b.postdate,
      })),
    ].filter((x) => x.title);

    res.setHeader("Cache-Control", "s-maxage=1800, stale-while-revalidate=3600");
    return res.status(200).json({ query: q, items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
