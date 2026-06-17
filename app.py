import datetime
import streamlit as st

st.set_page_config(
    page_title="ホロスコープ診断",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("✨ ホロスコープ診断")
st.caption("生年月日と出生地を入力すると、西洋占星術で強み・適職などを分析します。")

# ── サイドバー ─────────────────────────────────────────────────
with st.sidebar:
    st.header("設定")
    st.subheader("分析項目を選択")
    st.caption("強み10選・適職3選は常に表示されます。追加で知りたい項目にチェックを入れてください。")

    from modules import MODULES
    selected_ids = []
    for module in MODULES:
        # 強み・適職はルールベースで常に出すので非表示
        if module["id"] in ("strengths", "careers"):
            continue
        checked = st.checkbox(module["label"], value=module["default"], key=module["id"])
        if checked:
            selected_ids.append(module["id"])

    st.divider()
    st.subheader("追加で知りたいこと（自由記述）")
    custom_question = st.text_area(
        label="質問を自由に入力",
        placeholder="例: 海外移住との相性は？\n起業家としての素質はある？",
        height=120,
        help="Claude APIキーが設定されている場合のみ回答します。",
    )

# ── 入力フォーム ───────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    birth_date = st.date_input(
        "生年月日",
        value=datetime.date(1990, 1, 1),
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date.today(),
    )
with col2:
    use_time = st.checkbox("出生時刻を入力する", value=False)
    birth_time_input = st.time_input(
        "出生時刻（任意）",
        value=datetime.time(12, 0),
        step=60,
        disabled=not use_time,
        help="入力するとASC・ハウスも計算されより精度が上がります。",
    )

birth_place = st.text_input(
    "出生地",
    placeholder="例: Tokyo / Osaka / New York / Paris",
    help="英語表記の方が検索精度が上がります。",
)

with st.form("input_form"):
    submitted = st.form_submit_button("診断する", type="primary", use_container_width=True)

# ── 診断実行 ───────────────────────────────────────────────────
if submitted:
    if not birth_place.strip():
        st.error("出生地を入力してください。")
        st.stop()

    birth_time = birth_time_input if use_time else None

    with st.spinner("ホロスコープを計算中..."):
        try:
            from astro import build_chart
            chart = build_chart(birth_date, birth_time, birth_place.strip())
        except ValueError as e:
            st.error(str(e))
            st.stop()
        except Exception as e:
            st.error(f"ホロスコープ計算に失敗しました: {e}")
            st.stop()

    with st.expander("ホロスコープデータを確認する", expanded=False):
        from astro import chart_to_text
        st.code(chart_to_text(chart), language=None)

    st.divider()

    # ── ルールベースで強み・適職を表示（APIキー不要）──────────
    from analyzer import analyze
    result = analyze(chart)
    st.markdown(result)

    # ── APIキーがあれば追加モジュール・自由記述も処理 ──────────
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if api_key and (selected_ids or custom_question.strip()):
        st.divider()
        st.subheader("追加分析")
        try:
            from interpreter import stream_analysis
            st.write_stream(
                stream_analysis(chart, selected_ids, custom_question, api_key)
            )
        except Exception as e:
            st.error(f"追加分析でエラーが発生しました: {e}")
