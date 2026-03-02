# BINGO BINGO 分析工具

台灣彩券 BINGO BINGO 號碼分析 & 模擬投注系統。

## 功能

| 模組 | 說明 |
|------|------|
| 儀表板 | 最新預測總覽、近期開獎紀錄 |
| 基本玩法分析 | 1–10 星號碼頻率、命中率分析 |
| 超級號碼 | 超級獎號趨勢與推薦 |
| 猜大小 / 猜單雙 | 歷史比例、連續紀錄分析 |
| 進階分析 | 共現分析、尾數統計、區間分布、冷熱循環、連號偵測 |
| 智慧選號 | 綜合多維度推薦號碼組合 |
| 模擬投注 | 下注 → 自動兌獎 → 統計盈虧 |

### Session 隔離（模擬投注）

每個瀏覽器自動產生 UUID 存在 `localStorage`（key: `bingo_session_id`），透過 `X-Session-Id` header 隔離投注資料。**不需登入**，不同瀏覽器 / 無痕模式各自獨立。

## 技術架構

- **Backend**: FastAPI + SQLAlchemy + APScheduler + Gunicorn
- **Frontend**: Vue 3 + Vite + Pinia + Chart.js
- **Database**: SQLite（`backend/bingo.db`）
- **Deploy**: Nginx + systemd + Let's Encrypt

## 專案結構

```text
bingo_bingo/
├─ backend/
│  ├─ app/           # FastAPI 主程式、API routes、models
│  ├─ analysis/      # 分析引擎、兌獎引擎、賠率表
│  ├─ crawler/       # 台彩開獎資料爬蟲
│  ├─ scheduler/     # APScheduler 排程
│  ├─ scripts/       # 資料庫遷移腳本
│  └─ tests/         # pytest 測試
├─ frontend/
│  ├─ src/
│  │  ├─ views/      # 頁面元件
│  │  ├─ components/ # 共用元件（BetWidget、FrequencyChart 等）
│  │  ├─ stores/     # Pinia stores
│  │  └─ services/   # API 呼叫層（含 session interceptor）
│  └─ dist/          # 建置輸出
├─ deploy/           # 部署腳本與設定檔
└─ spec.md           # 規格文件
```

## 環境需求

- Python 3.10+
- Node.js 18+（建議 LTS）
- npm 9+

## 快速開始（本地開發）

### 1) 啟動後端

```powershell
cd backend
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

建立 `backend/.env`：

```env
DATABASE_URL=sqlite:///./bingo.db
CRAWLER_INTERVAL_MINUTES=6
CRAWLER_RELAX_TLS_STRICT=false
ENV=development
```

啟動 API：

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2) 啟動前端

```powershell
cd frontend
npm install
```

可選：建立 `frontend/.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

啟動：

```powershell
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

開啟瀏覽器：`http://127.0.0.1:5173/bingo_bingo/`

## API 總覽

| 端點 | 說明 |
|------|------|
| `GET /health` | 健康檢查 |
| `GET /api/draws/latest?limit=20` | 最近開獎紀錄 |
| `GET /api/draws/{term}` | 單一期號 |
| `GET /api/predictions/all?period_range=30` | 全部分析 |
| `POST /api/status/refresh` | 手動抓取刷新 |
| `GET /api/status/last-updated` | 最後更新時間 |
| `POST /api/simulation/bet` | 下注（需 `X-Session-Id`） |
| `GET /api/simulation/bets` | 投注紀錄（需 `X-Session-Id`） |
| `GET /api/simulation/stats` | 投注統計（需 `X-Session-Id`） |
| `POST /api/simulation/settle` | 手動兌獎（需 `X-Session-Id`） |
| `DELETE /api/simulation/bet/{id}` | 取消投注（需 `X-Session-Id`） |
| `GET /api/simulation/next-draw` | 下一期資訊 |

Swagger 文件：`http://127.0.0.1:8000/docs`

## 測試

```powershell
# 後端
cd backend
.\venv\Scripts\pytest -q

# 前端建置檢查
cd frontend
npm run build
```

## 部署

👉 詳見 [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md)

## 常見問題

### 前端顯示「暫無資料」

1. 確認後端啟動：`GET /health`
2. 觸發手動刷新：`POST /api/status/refresh`
3. 檢查資料：`GET /api/draws/latest?limit=5`

### TLS 憑證錯誤（抓取台彩 API）

在 `backend/.env` 設定：

```env
CRAWLER_RELAX_TLS_STRICT=true
```

