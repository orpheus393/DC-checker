// /api/movies — 미국 주말 박스오피스 (Box Office Mojo 스크래핑, 키 불필요)
//
// 공식 무료 API가 없어 Box Office Mojo 주말 차트 HTML을 서버에서 파싱합니다.
// 사이트 구조가 바뀌거나 접근이 막히면 502 → 화면이 샘플로 폴백합니다.

const cleanNum = (s) => Number(String(s).replace(/[^0-9]/g, "")) || 0;
const stripTags = (h) => h.replace(/<[^>]*>/g, "").trim();
const decode = (s) =>
  s.replace(/&amp;/g, "&").replace(/&#0?39;/g, "'").replace(/&quot;/g, '"')
   .replace(/&lt;/g, "<").replace(/&gt;/g, ">").trim();

export default async function handler(req, res) {
  const BOM = "https://www.boxofficemojo.com/weekend/";
  // BOM이 서버 IP를 막을 수 있어, 직접 → 공개 중계 프록시 순으로 시도.
  // (프록시가 BOM을 대신 받아오므로 차단을 우회. 모두 키 불필요)
  const attempts = [
    BOM,
    "https://api.allorigins.win/raw?url=" + encodeURIComponent(BOM),
    "https://corsproxy.io/?url=" + encodeURIComponent(BOM),
    "https://r.jina.ai/" + BOM,
  ];

  for (const url of attempts) {
    try {
      const r = await fetch(url, {
        headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
        signal: AbortSignal.timeout(9000),
      });
      if (!r.ok) continue;
      const html = await r.text();
      const items = parseBOM(html);
      if (items.length) {
        res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=21600");
        return res.status(200).json({ title: "미국 박스오피스", meta: "실시간 · Box Office Mojo (주말)", items });
      }
    } catch (e) { /* 다음 방법 시도 */ }
  }
  return res.status(502).json({ error: "박스오피스 데이터를 가져오지 못했습니다" });
}

function parseBOM(html) {
  const items = [];
  for (const block of html.split("<tr").slice(1)) {
    const cells = [...block.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((m) => m[1]);
    if (cells.length < 4) continue;                  // 헤더/빈 행 건너뜀
    const rank = cleanNum(stripTags(cells[0]));
    if (!rank) continue;

    const tm = block.match(/class="a-link-normal"[^>]*href="([^"]+)"[^>]*>([^<]+)</);
    if (!tm) continue;
    const title = decode(tm[2]);
    const link = "https://www.boxofficemojo.com" + tm[1].split("?")[0];

    const money = cells.map(stripTags).filter((v) => /^\$/.test(v));
    const weekend = money[0] || "";
    const total = money[money.length - 1] || "";

    items.push({
      title,
      sub: weekend ? `주말 매출 ${weekend}` : "박스오피스",
      link,
      linkLabel: "Box Office Mojo에서 보기",
      emoji: "🎬",
      change: 0,
      meta: [
        weekend && { k: "주말 매출", v: weekend },
        total && total !== weekend && { k: "누적 매출", v: total },
        { k: "순위", v: `${rank}위` },
      ].filter(Boolean),
    });
    if (items.length >= 10) break;
  }
  return items;
}
