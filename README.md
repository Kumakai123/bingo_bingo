# BINGO BINGO 分析工具

這是一個針對台灣彩券 BINGO BINGO 的分析工具，提供：

- 最新開獎資料抓取與儲存
- 基本玩法、超級號碼、猜大小、猜單雙分析
- 儀表板快速瀏覽與歷史紀錄
- 分析期數切換（含自訂期數）
- 手動刷新與自動輪詢更新

## 技術架構

- Backend: FastAPI + SQLAlchemy + APScheduler
- Frontend: Vue 3 + Vite + Pinia + Chart.js
- Database: SQLite（預設 `backend/bingo.db`）

## 專案結構

```text
bingo_bingo/
├─ backend/   # API, crawler, scheduler, tests
├─ frontend/  # Vue 前端頁面與元件
└─ spec.md    # 規格文件
```

## 環境需求

- Python 3.10+
- Node.js 18+（建議 LTS）
- npm 9+

## 快速開始（Windows PowerShell）

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

> 建議使用 `python -m uvicorn`，可避免 PowerShell 找不到 `uvicorn` 指令。

### 2) 啟動前端

```powershell
cd ..\frontend
npm install
```

可選：建立 `frontend/.env`（指定後端位址）

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

啟動前端：

```powershell
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

開啟瀏覽器：`http://127.0.0.1:5173`

## 使用方式

1. 進入儀表板查看最新預測與最近開獎紀錄。
2. 使用「分析期數」按鈕切換 5 / 10 / 20 / 30 / 50 / 100 或自訂期數。
3. 點右上角「手動刷新」可立即觸發後端抓取與分析。
4. 系統也會定時輪詢更新（前端）與排程抓取（後端，預設每 6 分鐘）。

## 常用 API

- 健康檢查: `GET /health`
- 最新開獎: `GET /api/draws/latest?limit=20`
- 單一期號: `GET /api/draws/{draw_term}`
- 全部分析: `GET /api/predictions/all?period_range=30`
- 手動刷新: `POST /api/status/refresh`
- 最後更新時間: `GET /api/status/last-updated`

Swagger 文件：`http://127.0.0.1:8000/docs`

## 驗證與測試

後端測試：

```powershell
cd backend
.\venv\Scripts\pytest -q
```

前端建置檢查：

```powershell
cd frontend
npm run build
```

## 常見問題

### 1) 前端顯示「暫無資料」

- 先確認後端是否啟動：`http://127.0.0.1:8000/health`
- 觸發手動刷新：`POST /api/status/refresh`
- 再檢查：`GET /api/draws/latest?limit=5`

### 2) 抓取台彩 API 失敗（TLS 憑證嚴格檢查）

可在 `backend/.env` 設定：

```env
CRAWLER_RELAX_TLS_STRICT=true
```

設定後重啟後端再測試。
