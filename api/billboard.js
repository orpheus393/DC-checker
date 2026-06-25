// /api/billboard — 빌보드 HOT 100 (공개 데이터셋, 키 불필요)
//
// 공식 API가 없어, 매일 자동 갱신되는 공개 JSON 데이터셋을 사용합니다.
// 접근이 막히면 502 → 화면이 샘플로 폴백합니다.

const SOURCE = "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/recent.json";

export default async function handler(req, res) {
  try {
    const r = await fetch(SOURCE, { signal: AbortSignal.timeout(8000) });
    if (!r.ok) throw new Error("dataset " + r.status);
    const d = await r.json();
    const items = (d.data || []).slice(0, 10).map((s) => ({
      title: s.song,
      sub: s.artist,
      emoji: "🏆",
      change: s.last_week == null ? "new" : s.last_week - s.this_week,
      meta: [
        s.peak_position && { k: "최고순위", v: s.peak_position + "위" },
        s.weeks_on_chart && { k: "차트인", v: s.weeks_on_chart + "주" },
      ].filter(Boolean),
    }));
    if (!items.length) throw new Error("empty");
    res.setHeader("Cache-Control", "s-maxage=21600, stale-while-revalidate=86400");
    return res.status(200).json({ title: "빌보드 HOT 100", meta: "실시간 · " + (d.date || ""), items });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
