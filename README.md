# ✨ ホロスコープ診断ツール

生年月日・出生地を入力するだけで、西洋占星術に基づく **強み10選・適職3選** を表示するWebアプリです。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 特徴

- **APIキー不要で基本診断が動作** — ルールベースエンジンで強み・適職を即表示
- **出生時刻なしでもOK** — 太陽・月・惑星から分析（時刻ありでASC・ハウスも追加）
- **Claude APIオプション** — APIキーを設定すると恋愛傾向・金運・自由記述質問も対応
- **世界中の地名に対応** — 英語表記の都市名で検索（Tokyo, Paris, New York など）

---

## セットアップ

### 1. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 2. （任意）Claude APIキーを設定

追加分析機能を使う場合は `.env` ファイルを作成してAPIキーを設定してください。

```bash
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

### 3. 起動

```bash
streamlit run app.py
```

ブラウザが自動で開き、`http://localhost:8501` でアプリにアクセスできます。

---

## 機能一覧

| 機能 | 必要なもの |
|------|-----------|
| 強み10選 | なし（無料） |
| 適職3選 | なし（無料） |
| 恋愛傾向 | Claude APIキー |
| 金運・財運 | Claude APIキー |
| 健康面の傾向 | Claude APIキー |
| 対人関係・コミュニケーション | Claude APIキー |
| 自由記述質問 | Claude APIキー |

---

## 技術スタック

- **UI**: [Streamlit](https://streamlit.io)
- **ホロスコープ計算**: [kerykeion](https://github.com/g-battaglia/kerykeion)（Swiss Ephemerisベース）
- **ジオコーディング**: [geopy](https://geopy.readthedocs.io/)（Nominatim）
- **タイムゾーン解決**: [timezonefinder](https://github.com/jannikmi/timezonefinder)
- **AI分析**: [Anthropic Claude API](https://www.anthropic.com/)（オプション）
