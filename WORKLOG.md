# ホロスコープ診断ツール — 作業ログ

---

## 2026-06-16 | 初回実装

### 要件定義

- **入力**: 生年月日・出生地・出生時刻（任意）
- **出力**: 強み10個 ＋ 適職3つ（後から項目追加できる拡張設計）
- **UI**: Streamlit（ブラウザで動くWebアプリ）
- **技術スタック**: Python + kerykeion + Claude API（claude-sonnet-4-6）

### 設計上の決定

| 決定事項 | 選択肢 | 理由 |
|---------|--------|------|
| ホロスコープ計算 | kerykeion | 無料・Swiss Ephemeris ベースで天文台レベルの精度。外部APIに依存しない |
| 解釈生成 | Claude API | プロンプト変更だけで分析内容を柔軟に拡張できる |
| ジオコーディング | geopy (Nominatim) | 無料・世界中の地名に対応 |
| タイムゾーン解決 | timezonefinder | 緯度経度からタイムゾーンを自動特定 |
| 出生時刻 | 任意入力 | 時刻不明でも太陽・月・惑星は計算可能。任意にすることで間口を広げる |
| 拡張設計 | modules.py | 辞書1つ追加するだけで新項目がUIに自動追加される |

### 作成ファイル

```
horoscope_tool/
├── app.py           # Streamlit UI（入力フォーム・結果表示・ストリーミング）
├── astro.py         # kerykeion でホロスコープ計算・日本語変換
├── interpreter.py   # Claude API 呼び出し・プロンプト生成
├── modules.py       # 分析モジュール定義（拡張ポイント）
├── requirements.txt
├── .env.example
└── WORKLOG.md       # 本ファイル
```

### 初期搭載モジュール（modules.py）

| ID | 表示名 | デフォルト |
|----|--------|-----------|
| strengths | 強み10選 | ON |
| careers | 適職3選 | ON |
| love | 恋愛傾向 | OFF |
| money | 金運・財運 | OFF |
| health | 健康面の傾向 | OFF |
| communication | 対人関係・コミュニケーション | OFF |

### 発生した問題と対処

**問題1: timezonefinder のビルド失敗**
- 原因: h3 パッケージのビルドに CMake が必要で失敗
- 対処: `timezonefinder==6.2.0`（h3 不要の旧バージョン）を指定

**問題2: kerykeion がサイン名を3文字略称で返す**
- 例: `"Taurus"` ではなく `"Tau"` で返ってくる
- 対処: `SIGN_JA` 辞書にフルネーム・略称の両方を登録

### 動作確認済み

- [x] Tokyo（1990-05-15 14:30）でホロスコープ計算 → 日本語で正常出力
- [x] ASC・MC・アスペクト（リリス含む）すべて日本語表示
- [x] Streamlit 起動確認（http://localhost:8502 → HTTP 200）
- [ ] Claude API 経由で強み・適職の実際の出力（APIキー必要）

---

## 2026-06-16 | 機能改善・ルールベース化・公開準備

### 改善1: UIの変更

| 変更内容 | 詳細 |
|---------|------|
| APIキーの非表示 | サイドバーのAPIキー入力欄を削除。`.env` ファイルからの自動読み込みのみに変更。配布先ユーザーにキーが見えない設計にした |
| 出生時刻の刻み | 15分刻み → 1分刻みに変更（`step=60` を追加） |

### 改善2: ルールベース分析エンジンの追加（APIキー完全不要）

**背景**: リストへの無料プレゼントとして配布するため、受け取ったユーザーがAPIキーなしで使える仕組みが必要になった。

**対応**: 占星術の知識をコードに組み込んだルールベースエンジンを新規実装。

**追加ファイル:**

| ファイル | 役割 |
|---------|------|
| `knowledge.py` | 全12サイン × 各惑星（太陽・月・ASC・水星・金星・火星・木星）の強み辞書 + 適職辞書 |
| `analyzer.py` | チャートデータから強み10個・適職3つを抽出してMarkdown形式で出力するエンジン |

**分析ロジック（強みの優先順位）:**

| 優先順位 | 天体 | 取得数 |
|---------|------|--------|
| 1 | 太陽 | 3つ |
| 2 | 月 | 2つ |
| 3 | ASC（出生時刻ありの場合） | 1つ |
| 4 | 水星 | 1つ |
| 5 | 金星 | 1つ |
| 6 | 火星 | 1つ |
| 7 | 支配元素 | 1つ |

**適職の選出順:**
1. 太陽サインから2つ
2. MC（出生時刻ありの場合）から補完
3. 支配元素から補完 → 合計3つ

**app.py の動作変更:**
- ルールベース分析を常時実行（APIキー不要）
- APIキーが `.env` に設定されている場合のみ、追加モジュール（恋愛傾向・金運等）と自由記述質問をClaude APIで処理

### 改善3: GitHub公開準備

- `.gitignore` を作成（`.env` ファイルがGitHubに上がらないよう保護）
- Streamlit Community Cloud での公開手順を確認済み

**公開手順（次回作業時）:**
1. `git init && git add . && git commit -m "initial commit"`
2. GitHubリポジトリを作成してpush
3. [share.streamlit.io](https://share.streamlit.io) でリポジトリを指定してDeploy

### 現在のファイル構成

```
horoscope_tool/
├── app.py           # Streamlit UI（ルールベース＋Claude API切り替え対応）
├── astro.py         # kerykeion でホロスコープ計算・日本語変換
├── analyzer.py      # ルールベース分析エンジン（APIキー不要）★新規
├── interpreter.py   # Claude API 呼び出し（追加モジュール用）
├── knowledge.py     # 占星術知識ベース（強み・適職辞書）★新規
├── modules.py       # 追加分析モジュール定義
├── requirements.txt
├── .env             # APIキー（Git管理外）
├── .env.example
├── .gitignore       # .envを除外 ★新規
└── WORKLOG.md
```

### 動作確認済み

- [x] ルールベース分析: Tokyo（1990-05-15 14:30）で強み10個・適職3つが正常出力
- [x] APIキーなしでアプリが正常起動・診断できること
- [x] 出生時刻なしでも動作すること（ASC省略・木星で補完）

---

## 2026-06-17 | Streamlit Cloud デプロイ・バグ修正

### 作業1: GitHub リポジトリ作成・公開設定

- `gh repo create` で `shamrock0429-stack/horoscope-tool` を作成（初期は Private）
- Streamlit Community Cloud の無料枠はパブリックリポジトリが必要なため Public に変更
- `.env`（APIキー）は `.gitignore` により除外済み、コミット対象外

### 作業2: Streamlit Cloud デプロイ時のビルドエラー解消

**エラー1: cffi ビルド失敗**
- 原因: `ffi.h` が見つからない（`libffi-dev` 未インストール）
- 対処: `packages.txt` を新規作成し `build-essential` / `libffi-dev` を追記

**エラー2: h3==3.7.7 CMake ビルド失敗**
- 原因: `timezonefinder==6.2.0` が `h3==3.7.7` を要求 → CMake < 3.5 の非互換
- 対処: `requirements.txt` を `timezonefinder>=6.5.0` に変更（6.5.0 以降 h3 が任意依存）

**エラー3: runtime.txt フォーマット誤り**
- 誤: `python-3.11` / 正: `3.11`（バージョン番号のみ）
- Streamlit Cloud は `python-X.Y` 形式を認識しない

**エラー4: swisseph Python 3.14 ABI 非互換**
- 原因: Streamlit Cloud が Python 3.14 を使用。swisseph の .so が `_ZSt7nothrow` を参照するが libstdc++ 側で未エクスポート
- 対処: `runtime.txt` を `3.12` に変更 → ただし **Reboot では反映されず、Delete & 再デプロイが必要**

### 作業3: アプリのバグ修正

**バグ1: 出生時刻チェックボックスが機能しない**
- 原因: `st.checkbox` と `st.time_input` を `st.form` 内に置いていたため、チェックしても即時再レンダリングされず `disabled` 状態が切り替わらなかった
- 対処: チェックボックス・時刻入力・出生地入力を `st.form` の外に移動。フォームには送信ボタンのみ残す

**バグ2: サイドバーがデフォルトで開いた状態**
- 対処: `st.set_page_config` に `initial_sidebar_state="collapsed"` を追加

### 現在のデプロイ状況

| 項目 | 状態 |
|------|------|
| GitHub リポジトリ | https://github.com/shamrock0429-stack/horoscope-tool |
| Streamlit URL | https://horoscope-tool-xdkwf6rg2k8hfjavm53a3s.streamlit.app/ |
| Python バージョン | `runtime.txt=3.12` 設定済み（要 Delete & 再デプロイで反映） |
| ビルドエラー | h3/cffi/swisseph 問題すべて対処済み |
| APIキー設定 | Streamlit Secrets（ANTHROPIC_API_KEY）への登録が必要 |

### Streamlit Secrets 設定手順

アプリの ⋮ → Settings → Secrets に以下を貼り付けて保存:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

---

## 今後の拡張候補

- **新モジュール追加案**（modules.py に辞書を追記するだけ）
  - 子育て傾向
  - リーダーシップスタイル
  - 学習スタイル・得意な勉強法
  - 海外・移住との相性
  - 起業家としての素質

- **UI改善候補**
  - ホロスコープチャート画像の表示（kerykeion の SVG 出力機能を使用）
  - 結果をPDFでダウンロード
  - 複数人の比較（シナストリー）

- **精度向上候補**
  - ドミナントプラネット（支配星）の計算
  - ステリウム（同一サインへの天体集中）の検出・強調

---

## 起動コマンド

```bash
cd /Users/seosachiko/dejiina_agent/horoscope_tool
streamlit run app.py
```
