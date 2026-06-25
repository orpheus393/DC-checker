// /api/movies — 미국 주말 박스오피스 (Box Office Mojo, 키 불필요)
//
// 1) /weekend/ 인덱스에서 가장 최근 주말 ID(예: 2025W25)를 찾고
// 2) 그 주말 상세 페이지의 영화 차트를 파싱한다.
// BOM이 서버 IP를 막을 수 있어 직접 → 공개 중계 프록시 순으로 받아온다(키 불필요).
// 사이트 구조 변경/차단 시 502 → 화면이 샘플로 폴백.

const cleanNum = (s) => Number(String(s).replace(/[^0-9]/g, "")) || 0;
const stripTags = (h) => h.replace(/<[^>]*>/g, "").trim();
const decode = (s) =>
  s.replace(/&amp;/g, "&").replace(/&#0?39;/g, "'").replace(/&quot;/g, '"')
   .replace(/&lt;/g, "<").replace(/&gt;/g, ">").trim();

// 직접 + 중계 프록시(원문 HTML 반환) 순으로 시도
async function fetchHtml(target) {
  const attempts = [
    target,
    "https://api.allorigins.win/raw?url=" + encodeURIComponent(target),
    "https://corsproxy.io/?url=" + encodeURIComponent(target),
  ];
  for (const url of attempts) {
    try {
      const r = await fetch(url, {
        headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
        signal: AbortSignal.timeout(9000),
      });
      if (!r.ok) continue;
      const t = await r.text();
      if (t && t.length > 1000) return t;
    } catch (e) { /* 다음 방법 */ }
  }
  throw new Error("fetch 실패: " + target);
}

function parseChart(html) {
  const items = [];
  for (const block of html.split("<tr").slice(1)) {
    const cells = [...block.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((m) => m[1]);
    if (cells.length < 5) continue;                       // 차트 행만
    const rank = cleanNum(stripTags(cells[0]));
    if (!rank) continue;

    // 영화 링크(/release/ 또는 /title/)만 제목으로 인정.
    // → 날짜(/weekend/)·배급사(/distributor/) 링크에 속지 않음.
    const tm = block.match(/href="(\/(?:release|title)\/[^"]+)"[^>]*>([^<]+)</);
    if (!tm) continue;
    const title = decode(tm[2]);
    if (!title) continue;
    const link = "https://www.boxofficemojo.com" + tm[1].split("?")[0];

    const money = cells.map(stripTags).filter((v) => /^\$/.test(v));
    const weekend = money[0] || "";
    const total = money[money.length - 1] || "";

    items.push({
      title,
      sub: weekend ? `주말 매출 ${weekend}` : `${rank}위`,
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

export default async function handler(req, res) {
  try {
    // 1) 최근 주말 ID 찾기
    const index = await fetchHtml("https://www.boxofficemojo.com/weekend/");
    const m = index.match(/\/weekend\/(\d{4}W\d{1,2})\//);
    const chartUrl = m
      ? `https://www.boxofficemojo.com/weekend/${m[1]}/`
      : "https://www.boxofficemojo.com/weekend/";

    // 2) 해당 주말의 영화 차트 파싱
    const html = await fetchHtml(chartUrl);
    const items = parseChart(html);
    if (!items.length) throw new Error("파싱 결과 없음");

    res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=21600");
    return res.status(200).json({ title: "미국 박스오피스", meta: "실시간 · Box Office Mojo (주말)", items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
