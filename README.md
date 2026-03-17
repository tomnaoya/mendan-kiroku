# 面談記録システム

パルスサーベイの結果をもとに、スタッフの面談記録を管理するWebアプリです。

## 技術スタック

| 層 | 技術 |
|----|------|
| バックエンド | Python / FastAPI |
| テンプレート | Jinja2 |
| DB | PostgreSQL（Render）/ SQLite（ローカル） |
| ORM | SQLAlchemy |
| フロントエンド | Bootstrap 5 + Chart.js |
| デプロイ | Render |

---

## ローカル開発

```bash
# 1. リポジトリをクローン
git clone <your-repo-url>
cd pulse-survey-app

# 2. 仮想環境を作成・有効化
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 環境変数を設定
cp .env.example .env

# 5. DBの初期化＆シードデータ投入
python init_db.py

# 6. サーバー起動
uvicorn app.main:app --reload
```

ブラウザで http://localhost:8000 を開く。
- ID: `admin`  /  PW: `admin`

---

## Render へのデプロイ

### 初回セットアップ

1. [Render](https://render.com) にサインアップ
2. GitHub リポジトリを push（下記参照）
3. Render ダッシュボード → **"New"** → **"Blueprint"**
4. 対象リポジトリを選択 → `render.yaml` を自動検出してデプロイ

Render が自動で以下を行います：
- PostgreSQL データベース（`pulse-survey-db`）の作成
- `pip install -r requirements.txt` によるビルド
- `python init_db.py` によるテーブル作成＆シード投入
- `uvicorn` でのアプリ起動

### GitHub へのコードプッシュ

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/tomnaoya/mendan-kiroku.git
git push -u origin main
```

---

## 画面構成

| 画面 | URL | 説明 |
|------|-----|------|
| ログイン | `/login` | ID/PW認証 |
| 一覧 | `/staff` | 全スタッフ・直近スコア一覧、部門フィルター |
| 詳細 | `/staff/{id}` | スコア推移グラフ＋月次面談入力フォーム |

---

## DB構成

```
staff
  id, name, department

survey_records
  id, staff_id, year, month
  score_work, score_human, score_health
  survey_comment, response_date

interview_records
  id, staff_id, year, month
  interview_date, interviewer, location, duration
  q1_content, q2_content, q3_content
  overall_findings, improvement_policy, other_notes
```

---

## 環境変数（Render 設定）

| 変数 | 説明 |
|------|------|
| `DATABASE_URL` | Render PostgreSQL の接続URL（自動設定） |
| `SECRET_KEY` | セッション暗号化キー（Renderが自動生成） |
| `ADMIN_ID` | ログインID（デフォルト: `admin`） |
| `ADMIN_PW` | ログインPW（デフォルト: `admin`）← **本番では必ず変更** |
