# BINGO BINGO 部署指南

Ubuntu EC2 (or any Ubuntu server) 部署，使用 Nginx + Gunicorn + systemd + Let's Encrypt。

## 前置條件

- Ubuntu 20.04+ 主機（EC2、VPS 等）
- 域名已指向該主機 IP
- SSH 存取權限

## 一鍵部署（首次）

```bash
# 1. Clone 到 /home/ubuntu/bingo_bingo
cd /home/ubuntu
git clone <your-repo-url> bingo_bingo

# 2. 執行部署腳本
cd bingo_bingo
sudo bash deploy/deploy.sh your-domain.com
```

腳本會自動完成：

| 步驟 | 動作 |
|------|------|
| 1 | 安裝系統套件（Python, Node.js 20, Nginx, Certbot） |
| 2 | 建立 Python venv，安裝 pip 依賴 + Gunicorn |
| 3 | 安裝 systemd service（`bingo-backend.service`） |
| 4 | `npm install` + `npm run build`（前端打包） |
| 5 | 設定 Nginx reverse proxy + static files |
| 6 | 申請 Let's Encrypt SSL 憑證 |
| 7 | 驗證服務狀態 |

## 檔案說明

```text
deploy/
├─ deploy.sh                # 一鍵部署腳本
├─ update.sh                # 快速更新腳本（git pull 後使用）
├─ bingo-backend.service    # systemd 服務設定
├─ nginx-bingo.conf         # Nginx 設定模板
└─ env.backend.example      # backend/.env 範例
```

## 環境變數

`backend/.env`（部署腳本會自動從 `env.backend.example` 建立）：

```env
DATABASE_URL=sqlite:///./bingo.db
CRAWLER_INTERVAL_MINUTES=6
ENV=production
ALLOWED_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]
```

`frontend/.env.production`（部署腳本會自動建立）：

```env
VITE_API_BASE_URL=https://your-domain.com
```

## 更新部署

```bash
cd /home/ubuntu/bingo_bingo
git pull
sudo bash deploy/update.sh
```

`update.sh` 會自動：
1. 安裝新 pip 依賴
2. 重啟 backend service
3. 重新 `npm install` + `npm run build`
4. Reload Nginx

## 資料庫遷移

新增 Session 隔離功能需要跑一次 migration（已有的 `simulated_bets` 資料表需加上 `session_id` 欄位）：

```bash
cd /home/ubuntu/bingo_bingo/backend
source venv/bin/activate
python -m scripts.migrate_add_session_id
```

> 此腳本 **冪等**，重複執行不會出錯。既有投注紀錄會標記為 `session_id='legacy'`。

## 服務管理

```bash
# 查看後端狀態
sudo systemctl status bingo-backend

# 重啟後端
sudo systemctl restart bingo-backend

# 查看即時 log
sudo journalctl -u bingo-backend -f

# 測試 Nginx 設定
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## 架構圖

```
                    ┌──────────────────────┐
                    │       Browser        │
                    │  (localStorage UUID) │
                    └──────────┬───────────┘
                               │ HTTPS
                    ┌──────────▼───────────┐
                    │        Nginx         │
                    │  :80 / :443 (SSL)    │
                    ├──────────────────────┤
                    │  /bingo_bingo/*      │──→  Static files (frontend/dist/)
                    │  /api/*              │──→  Gunicorn :8000
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Gunicorn + Uvicorn  │
                    │  (2 workers)         │
                    ├──────────────────────┤
                    │  FastAPI App         │
                    │  ├─ /api/draws/      │
                    │  ├─ /api/predictions/│
                    │  ├─ /api/simulation/ │ ← X-Session-Id header
                    │  └─ /api/status/     │
                    ├──────────────────────┤
                    │  APScheduler         │
                    │  (每 6 分鐘爬蟲)      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   SQLite (bingo.db)  │
                    └──────────────────────┘
```

## Troubleshooting

### Backend 啟動失敗

```bash
sudo journalctl -u bingo-backend --no-pager -n 50
```

### Certbot 失敗

確認 DNS A record 已指向此主機 IP，然後手動重試：

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 前端 404

確認 `vite.config.js` 的 `base` 設定為 `/bingo_bingo/`，且 Nginx `alias` 指向正確的 `dist/` 路徑。
