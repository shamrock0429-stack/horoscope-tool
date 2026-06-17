from typing import Generator
import anthropic
from astro import chart_to_text


def stream_analysis(
    chart: dict,
    selected_module_ids: list[str],
    custom_question: str,
    api_key: str,
) -> Generator[str, None, None]:
    from modules import MODULES

    chart_text = chart_to_text(chart)

    # 選択されたモジュールのプロンプトを結合
    module_map = {m["id"]: m for m in MODULES}
    sections = []
    for mid in selected_module_ids:
        if mid in module_map:
            sections.append(module_map[mid]["prompt"])

    # ユーザーが追加した自由記述の質問
    if custom_question.strip():
        sections.append(
            f"追加の質問:\n{custom_question.strip()}\n\n"
            "上記の質問にも、このホロスコープデータに基づいて日本語で回答してください。"
        )

    if not sections:
        yield "分析項目が選択されていません。"
        return

    sections_text = "\n\n---\n\n".join(sections)

    prompt = f"""あなたは西洋占星術の専門家です。
以下のホロスコープデータをもとに、指定された各項目について日本語で詳しく分析してください。
占星術的な根拠（どの天体・サイン・ハウス・アスペクトから判断したか）を必ず示してください。

【ホロスコープデータ】
{chart_text}

【分析項目と出力形式】
{sections_text}
"""

    client = anthropic.Anthropic(api_key=api_key)
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
