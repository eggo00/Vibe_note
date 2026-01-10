# Quick Start Guide

**Feature**: Vibe Coding AI 學霸筆記生成器
**Last Updated**: 2026-01-07

## 環境需求

- **Python**: 3.11+
- **Node.js**: 18+
- **Git**: 最新版本
- **Docker** (可選): 用於快速啟動環境
- **作業系統**: macOS, Linux, Windows (WSL2)

---

## 快速啟動（5 分鐘）

### 方法 1：使用 Docker (推薦)

```bash
# 1. Clone 專案
git clone https://github.com/your-org/vibe-note.git
cd vibe-note

# 2. 啟動 Docker Compose
docker-compose up -d

# 3. 開啟瀏覽器
# 前端: http://localhost:3000
# 後端 API 文件: http://localhost:8000/docs
```

### 方法 2：本地開發環境

#### 2.1 後端設定

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 複製環境變數範例
cp .env.example .env

# 編輯 .env 設定（務必填入 OPENAI_API_KEY）
nano .env

# 初始化資料庫
python scripts/init_db.py

# 啟動後端伺服器
python src/main.py
```

後端預設運行於 `http://localhost:8000`

#### 2.2 前端設定

```bash
# 開啟新終端，進入前端目錄
cd frontend

# 安裝依賴
npm install

# 複製環境變數
cp .env.example .env

# 啟動開發伺服器
npm run dev
```

前端預設運行於 `http://localhost:3000`

---

## 環境變數設定

### 後端 (`.env`)

```bash
# 必填：OpenAI API Key
OPENAI_API_KEY=sk-...your-key-here

# 資料庫路徑（SQLite）
DATABASE_URL=sqlite:///./vibe_note.db

# 伺服器設定
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 爬蟲設定
RATE_LIMIT_PER_SECOND=1
SCRAPER_TIMEOUT=30
USER_AGENT=VibeCodingNoteBot/1.0

# 匯出檔案路徑
EXPORT_DIR=/tmp/exports

# 資料保留天數
DATA_RETENTION_DAYS=30
```

### 前端 (`.env`)

```bash
# API 端點
REACT_APP_API_URL=http://localhost:8000

# 自動儲存間隔（毫秒）
REACT_APP_AUTO_SAVE_INTERVAL=30000

# LocalStorage 備份啟用
REACT_APP_LOCAL_BACKUP_ENABLED=true
```

---

## API 文件

後端啟動後，存取以下網址查看完整 API 文件：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 手動測試流程

### 測試 1：Notion 爬取 → 筆記生成

```bash
# 1. 匯入 Notion 頁面
curl -X POST http://localhost:8000/api/notion/import \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.notion.so/your-page-url"}'

# 回應範例：
# {
#   "success": true,
#   "data": {
#     "source_id": "src-456def",
#     "learnable_blocks": 12
#   }
# }

# 2. 分析內容品質
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type": application/json" \
  -d '{"source_id": "src-456def"}'

# 3. 生成筆記
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_md": "# 對話紀錄\n\n...",
    "data_source_ids": ["src-456def"]
  }'

# 回應範例：
# {
#   "success": true,
#   "data": {
#     "document_id": "550e8400...",
#     "title": "React Hooks 實作筆記",
#     "content": "# 專案摘要\n\n..."
#   }
# }

# 4. 取得筆記內容
curl http://localhost:8000/api/doc/550e8400...
```

### 測試 2：線上編輯與版本管理

```bash
# 1. 開啟前端編輯器
# 前往 http://localhost:3000/editor/550e8400...

# 2. 在編輯器中修改內容，等待 30 秒自動儲存
# 或手動點擊「儲存」按鈕

# 3. 測試 undo/redo
# Ctrl+Z (undo), Ctrl+Shift+Z (redo)

# 4. 查看版本歷史
curl http://localhost:8000/api/doc/550e8400.../versions

# 5. 還原到舊版本
curl -X POST http://localhost:8000/api/doc/550e8400.../restore \
  -H "Content-Type: application/json" \
  -d '{"version_id": "v-123abc"}'
```

### 測試 3：匯出功能

```bash
# 匯出為 PDF
curl -X POST http://localhost:8000/api/doc/550e8400.../export \
  -H "Content-Type: application/json" \
  -d '{"format": "pdf"}' \
  -o note.pdf

# 匯出為 HTML
curl -X POST http://localhost:8000/api/doc/550e8400.../export \
  -H "Content-Type: application/json" \
  -d '{"format": "html"}' \
  -o note.html
```

---

## 常見問題

### Q1: OpenAI API 呼叫失敗

**錯誤訊息**: `"OpenAI API key not configured"`

**解決方法**:
1. 確認 `.env` 檔案中 `OPENAI_API_KEY` 已正確設定
2. 重新啟動後端伺服器
3. 檢查 API Key 是否有效：
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

### Q2: 爬蟲失敗（403 Forbidden）

**可能原因**:
- Notion 頁面未設為公開
- 網站封鎖爬蟲 User-Agent
- 超過 rate limit

**解決方法**:
1. 確認 Notion 頁面設定為「公開存取」
2. 檢查 `robots.txt` 是否允許爬取
3. 使用「手動貼上」fallback 功能

### Q3: 前端無法連接後端

**錯誤訊息**: `"Network Error" or "CORS error"`

**解決方法**:
1. 確認後端已啟動：`curl http://localhost:8000/docs`
2. 檢查前端 `.env` 的 `REACT_APP_API_URL` 設定
3. 檢查後端 CORS 設定（`src/main.py` 中的 `allow_origins`）

### Q4: 資料庫初始化失敗

**解決方法**:
```bash
# 刪除舊資料庫
rm vibe_note.db

# 重新初始化
python scripts/init_db.py

# 檢查資料表是否建立
sqlite3 vibe_note.db ".tables"
```

### Q5: PDF 匯出失敗

**錯誤訊息**: `"Puppeteer not found"`

**解決方法**:
```bash
# 安裝 Puppeteer
pip install pyppeteer

# 下載 Chromium（首次執行時自動下載）
python -c "import pyppeteer; pyppeteer.install()"
```

---

## 開發工作流程

### 1. 建立新功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 修改程式碼

- **後端**: 修改 `backend/src/` 下的檔案
- **前端**: 修改 `frontend/src/` 下的檔案

### 3. 手動測試

參考上方「手動測試流程」，確保功能正常運作。

### 4. 更新 API 文件

若新增或修改 API，更新 `specs/001-ai-note-generator/contracts/openapi.yaml`

### 5. Commit 與 Push

```bash
git add .
git commit -m "新增 XXX 功能"
git push origin feature/your-feature-name
```

---

## 專案結構速覽

```
.
├── backend/          # Python FastAPI 後端
│   ├── src/          # 原始碼
│   │   ├── main.py   # 應用程式入口
│   │   ├── models/   # 資料模型（SQLAlchemy）
│   │   ├── services/ # 業務邏輯（爬蟲、分析、生成）
│   │   ├── api/      # API 路由
│   │   └── schemas/  # Pydantic schemas
│   └── requirements.txt
│
├── frontend/         # React 前端
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/    # 頁面元件
│   │   ├── components/ # 可重用元件
│   │   └── services/ # API 呼叫
│   └── package.json
│
├── specs/            # 功能規格與設計文件
│   └── 001-ai-note-generator/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       └── contracts/
│
├── scripts/          # 工具腳本
│   ├── init_db.py
│   └── cleanup_old_data.py
│
├── docker-compose.yml
└── README.md
```

---

## 下一步

- 閱讀 [API 文件](http://localhost:8000/docs) 了解所有端點
- 查看 [data-model.md](./data-model.md) 了解資料庫結構
- 參考 [research.md](./research.md) 了解技術選型決策
- 執行 `/speckit.tasks` 產生開發任務清單

---

## 取得協助

- **GitHub Issues**: https://github.com/your-org/vibe-note/issues
- **文件問題**: 查看 `specs/` 目錄下的設計文件
- **API 問題**: 參考 Swagger UI 的範例與 schema

Happy Coding! 🚀
