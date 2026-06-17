import datetime
from typing import Optional

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from kerykeion import AstrologicalSubject

SIGN_JA = {
    # フルネーム
    "Aries": "牡羊座", "Taurus": "牡牛座", "Gemini": "双子座",
    "Cancer": "蟹座", "Leo": "獅子座", "Virgo": "乙女座",
    "Libra": "天秤座", "Scorpio": "蠍座", "Sagittarius": "射手座",
    "Capricorn": "山羊座", "Aquarius": "水瓶座", "Pisces": "魚座",
    # kerykeion が返す3文字略称
    "Ari": "牡羊座", "Tau": "牡牛座", "Gem": "双子座",
    "Can": "蟹座", "Leo": "獅子座", "Vir": "乙女座",
    "Lib": "天秤座", "Sco": "蠍座", "Sag": "射手座",
    "Cap": "山羊座", "Aqu": "水瓶座", "Pis": "魚座",
}

ELEMENT_JA = {"Fire": "火", "Earth": "土", "Air": "風", "Water": "水"}
MODALITY_JA = {"Cardinal": "活動", "Fixed": "不動", "Mutable": "柔軟"}

ASPECT_JA = {
    "conjunction": "合（コンジャンクション）",
    "opposition": "衝（オポジション）",
    "trine": "トライン",
    "square": "スクエア",
    "sextile": "セクスタイル",
}

PLANET_JA = {
    "Sun": "太陽", "Moon": "月", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
    "Uranus": "天王星", "Neptune": "海王星", "Pluto": "冥王星",
    "Mean_Node": "ノース・ノード", "True_Node": "ノース・ノード",
    "Mean_Lilith": "リリス", "True_Lilith": "リリス",
    "Chiron": "キロン", "Juno": "ジュノー",
}


def geocode_location(place_name: str) -> tuple[float, float, str]:
    geolocator = Nominatim(user_agent="horoscope_strength_tool_v1", timeout=10)
    location = geolocator.geocode(place_name, language="en")
    if not location:
        raise ValueError(
            f"出生地「{place_name}」が見つかりませんでした。"
            "英語表記や都市名で再入力してください（例: Tokyo, Osaka, New York）。"
        )
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=location.latitude, lng=location.longitude)
    if not tz_str:
        raise ValueError("タイムゾーンを特定できませんでした。より具体的な地名を入力してください。")
    return location.latitude, location.longitude, tz_str


def _safe_sign_ja(sign_en: str) -> str:
    return SIGN_JA.get(sign_en, sign_en)


def _safe_house_label(house_str: str) -> str:
    # kerykeion returns e.g. "First_House" or "First House"
    normalized = house_str.replace("_", " ")
    order = [
        "First", "Second", "Third", "Fourth", "Fifth", "Sixth",
        "Seventh", "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth",
    ]
    for i, name in enumerate(order, 1):
        if name in normalized:
            return f"第{i}ハウス"
    return house_str


def build_chart(
    birth_date: datetime.date,
    birth_time: Optional[datetime.time],
    place_name: str,
) -> dict:
    lat, lng, tz_str = geocode_location(place_name)

    hour = birth_time.hour if birth_time else 12
    minute = birth_time.minute if birth_time else 0

    subject = AstrologicalSubject(
        name="User",
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=hour,
        minute=minute,
        lat=lat,
        lng=lng,
        tz_str=tz_str,
        online=False,
    )

    planet_attrs = [
        ("太陽", subject.sun),
        ("月", subject.moon),
        ("水星", subject.mercury),
        ("金星", subject.venus),
        ("火星", subject.mars),
        ("木星", subject.jupiter),
        ("土星", subject.saturn),
        ("天王星", subject.uranus),
        ("海王星", subject.neptune),
        ("冥王星", subject.pluto),
    ]

    elements: dict[str, int] = {}
    modalities: dict[str, int] = {}
    planet_data: dict[str, str] = {}

    for ja_name, planet in planet_attrs:
        sign = _safe_sign_ja(planet.sign)
        element = ELEMENT_JA.get(planet.element, planet.element)
        modality = MODALITY_JA.get(planet.quality, planet.quality)
        retro = "（逆行）" if planet.retrograde else ""

        try:
            house = _safe_house_label(planet.house)
            planet_data[ja_name] = f"{sign} {house}{retro}"
        except Exception:
            planet_data[ja_name] = f"{sign}{retro}"

        elements[element] = elements.get(element, 0) + 1
        modalities[modality] = modalities.get(modality, 0) + 1

    dominant_element = max(elements, key=elements.get)
    dominant_modality = max(modalities, key=modalities.get)

    # ASC / MC（出生時刻ありの場合のみ意味を持つ）
    asc_sign = None
    mc_sign = None
    if birth_time:
        try:
            asc_sign = _safe_sign_ja(subject.first_house.sign)
            mc_sign = _safe_sign_ja(subject.tenth_house.sign)
        except Exception:
            pass

    # アスペクト計算
    aspects_str = ""
    try:
        from kerykeion import NatalAspects
        nat = NatalAspects(subject)
        asp_list = []
        for asp in (nat.relevant_aspects or [])[:8]:
            p1 = PLANET_JA.get(asp.get("p1_name", ""), asp.get("p1_name", ""))
            p2 = PLANET_JA.get(asp.get("p2_name", ""), asp.get("p2_name", ""))
            a = ASPECT_JA.get(asp.get("aspect", ""), asp.get("aspect", ""))
            asp_list.append(f"{p1} {a} {p2}")
        aspects_str = "、".join(asp_list)
    except Exception:
        aspects_str = "（計算できませんでした）"

    return {
        "planets": planet_data,
        "asc": asc_sign,
        "mc": mc_sign,
        "dominant_element": dominant_element,
        "dominant_modality": dominant_modality,
        "aspects": aspects_str,
        "has_birth_time": birth_time is not None,
        "place": place_name,
        "birth_date": birth_date.strftime("%Y年%m月%d日"),
    }


def chart_to_text(chart: dict) -> str:
    lines = [f"生年月日: {chart['birth_date']}  出生地: {chart['place']}"]
    if not chart["has_birth_time"]:
        lines.append("※ 出生時刻不明のため、ASC・MCは省略（太陽・月・惑星のみ）")
    lines.append("")

    for name, info in chart["planets"].items():
        lines.append(f"・{name}: {info}")

    if chart.get("asc"):
        lines.append(f"・ASC（アセンダント）: {chart['asc']}")
    if chart.get("mc"):
        lines.append(f"・MC（天頂）: {chart['mc']}")

    lines.append(f"・支配元素: {chart['dominant_element']}")
    lines.append(f"・支配モダリティ: {chart['dominant_modality']}")
    if chart["aspects"]:
        lines.append(f"・主要アスペクト: {chart['aspects']}")

    return "\n".join(lines)
