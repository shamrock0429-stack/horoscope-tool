"""APIキー不要のルールベース分析エンジン。"""

from knowledge import SIGNS, STRENGTHS, ELEMENT_STRENGTHS, CAREERS


def extract_sign(planet_info: str) -> str:
    """'牡牛座 第8ハウス' のような文字列からサイン名を取り出す。"""
    for sign in SIGNS:
        if planet_info.startswith(sign):
            return sign
    return ""


def analyze(chart: dict) -> str:
    planets = chart.get("planets", {})
    asc = chart.get("asc")
    mc = chart.get("mc")
    element = chart.get("dominant_element", "")

    strengths: list[dict] = []

    def add(key: tuple, limit: int, source_label: str) -> None:
        for s in STRENGTHS.get(key, [])[:limit]:
            strengths.append({**s, "source": source_label})

    # 1. 太陽 × 3
    sun_sign = extract_sign(planets.get("太陽", ""))
    add(("sun", sun_sign), 3, f"太陽（{sun_sign}）")

    # 2. 月 × 2
    moon_sign = extract_sign(planets.get("月", ""))
    add(("moon", moon_sign), 2, f"月（{moon_sign}）")

    # 3. ASC × 1（出生時刻ありの場合のみ）
    if asc:
        add(("asc", asc), 1, f"ASC（{asc}）")

    # 4. 水星 × 1
    mercury_sign = extract_sign(planets.get("水星", ""))
    add(("mercury", mercury_sign), 1, f"水星（{mercury_sign}）")

    # 5. 金星 × 1
    venus_sign = extract_sign(planets.get("金星", ""))
    add(("venus", venus_sign), 1, f"金星（{venus_sign}）")

    # 6. 火星 × 1
    mars_sign = extract_sign(planets.get("火星", ""))
    add(("mars", mars_sign), 1, f"火星（{mars_sign}）")

    # 7. 支配元素 × 1
    for s in ELEMENT_STRENGTHS.get(element, [])[:1]:
        strengths.append({**s, "source": f"支配元素（{element}）"})

    # 8. ASCがない場合は木星で補完
    if not asc and len(strengths) < 10:
        jupiter_sign = extract_sign(planets.get("木星", ""))
        add(("jupiter", jupiter_sign), 10 - len(strengths), f"木星（{jupiter_sign}）")

    strengths = strengths[:10]

    # ── 適職 ──────────────────────────────────────────────────────
    careers: list[dict] = []
    seen_jobs: set[str] = set()

    def add_career(key: tuple, limit: int) -> None:
        for c in CAREERS.get(key, []):
            if c["job"] not in seen_jobs and len(careers) < limit:
                careers.append(c)
                seen_jobs.add(c["job"])

    add_career(("sun", sun_sign), 2)

    if mc:
        add_career(("mc", mc), 3)

    add_career(("element", element), 3)

    careers = careers[:3]

    return _format(strengths, careers, chart)


def _format(strengths: list[dict], careers: list[dict], chart: dict) -> str:
    lines: list[str] = []

    # ヘッダー情報
    lines.append(f"**生年月日:** {chart.get('birth_date', '')}　**出生地:** {chart.get('place', '')}")
    if not chart.get("has_birth_time"):
        lines.append("_※ 出生時刻が不明のため、ASC・ハウスは省略しています。_")
    lines.append("")

    # 強み
    lines.append("## あなたの強み10選\n")
    for i, s in enumerate(strengths, 1):
        lines.append(f"### {i}. {s['title']}")
        lines.append(f"_{s['source']}_\n")
        lines.append(f"{s['detail']}\n")

    lines.append("---\n")

    # 適職
    lines.append("## あなたの適職3選\n")
    for i, c in enumerate(careers, 1):
        lines.append(f"### {i}. {c['job']}")
        reason = c.get("reason") or c.get("detail", "")
        lines.append(f"{reason}\n")

    return "\n".join(lines)
