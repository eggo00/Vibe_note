# Vibe Note - AI 學霸筆記生成器

> 從 Vibe Coding 學習過程自動產出高品質圖文開發筆記

## 專案簡介

Vibe Note 是一個 AI 驅動的學習筆記自動生成系統，幫助 Vibe Coding 學員快速整理作業與學習筆記。

### 核心功能

- 📝 **自動爬取分析**：從 Notion 作業、GitHub Repo、老師 Blog 爬取內容並進行品質評分
- 🎨 **風格學習**：分析老師寫作風格，生成符合老師要求的筆記
- ✏️ **線上編輯**：提供 Markdown 編輯器，支援 undo/redo、版本管理、即時預覽
- 📤 **多格式匯出**：支援 Markdown、HTML、PDF 匯出與一鍵複製

### 技術棧

**後端**:
- Python 3.11+ / FastAPI
- SQLAlchemy (SQLite)
- Beautiful Soup / Playwright (爬蟲)
- OpenAI API (內容分析與生成)

**前端**:
- React 18 / TypeScript
- Vite
- Monaco Editor (程式碼編輯器)
- Axios

## 快速開始

### 環境需求

- Python 3.11+
- Node.js 18+
- Docker (可選)

### 方法 1: 使用 Docker (推薦)

\`\`\`bash
# 1. Clone 專案
git clone https://github.com/your-org/vibe-note.git
cd vibe-note

# 2. 複製環境變數範例
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. 編輯 backend/.env 填入 OpenAI API Key
# OPENAI_API_KEY=sk-...your-key-here

# 4. 啟動服務
docker-compose up -d

# 5. 開啟瀏覽器
# 前端: http://localhost:3000
# 後端 API 文件: http://localhost:8000/docs
\`\`\`

### 方法 2: 本地開發

#### 後端設定

\`\`\`bash
cd backend

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 安裝依賴
pip install -r requirements.txt

# 複製並設定環境變數
cp .env.example .env
# 編輯 .env 填入 OPENAI_API_KEY

# 初始化資料庫
python ../scripts/init_db.py

# 啟動後端
python src/main.py
\`\`\`

#### 前端設定

\`\`\`bash
cd frontend

# 安裝依賴
npm install

# 複製環境變數
cp .env.example .env

# 啟動開發伺服器
npm run dev
\`\`\`

## 專案結構

\`\`\`
.
├── backend/              # Python FastAPI 後端
│   ├── src/
│   │   ├── models/       # 資料模型
│   │   ├── services/     # 業務邏輯（爬蟲、分析、生成）
│   │   ├── api/          # API 路由
│   │   └── schemas/      # Pydantic schemas
│   └── requirements.txt
│
├── frontend/             # React 前端
│   ├── src/
│   │   ├── pages/        # 頁面元件
│   │   ├── components/   # 可重用元件
│   │   └── services/     # API 呼叫
│   └── package.json
│
├── specs/                # 功能規格與設計文件
│   └── 001-ai-note-generator/
│       ├── spec.md
│       ├── plan.md
│       ├── data-model.md
│       └── tasks.md
│
├── scripts/              # 工具腳本
│   └── init_db.py        # 資料庫初始化
│
├── docs/                 # 專案文件
├── docker-compose.yml
└── README.md
\`\`\`

## 使用說明

### 1. 輸入資料來源

在首頁輸入以下資訊：
- Notion 公開作業連結（1-3 個）
- 對話紀錄 Markdown 檔案
- GitHub Repo URL（可選）
- 老師 Blog URL（可選）

### 2. 系統分析

系統會自動：
- 爬取 Notion 內容並進行 block-level 品質評分
- 分析老師 Blog 寫作風格
- 讀取 GitHub Repo README 與主要程式碼

### 3. 生成筆記

點擊「開始分析」後，系統會產出包含以下段落的 Markdown 筆記：
- 專案摘要
- 核心功能說明
- 關鍵程式碼與解說
- 常見錯誤與解法

### 4. 編輯與匯出

在編輯器中：
- 修改內容（自動儲存）
- 使用 Ctrl+Z / Ctrl+Shift+Z 進行 undo/redo
- 查看版本歷史並還原
- 匯出為 Markdown / HTML / PDF

## API 文件

後端啟動後，存取以下網址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 開發指南

### 手動測試

參考 `docs/api-manual-tests.md` 與 `docs/e2e-test-scenarios.md`

### 憲章與原則

本專案遵循以下開發原則（詳見 `.specify/memory/constitution.md`）：

1. **MVP 優先開發**：快速迭代，避免過度設計
2. **使用者體驗至上**：直觀易用，友善錯誤處理
3. **程式碼簡潔**：保持簡單，遵循 YAGNI
4. **資料隱私**：遵守 robots.txt，30 天自動刪除
5. **容錯設計**：優雅降級，提供 fallback

### 不實作測試

本專案 MVP 階段不撰寫自動化測試，以手動 E2E 測試為主。

## 資料隱私

- 遵守 robots.txt 規範
- 不爬取需登入或付費內容
- 所有資料 30 天後自動刪除
- 不儲存個人身份資訊

## 授權

MIT License

## 貢獻指南

歡迎提交 Issue 或 Pull Request！

## 聯絡方式

- GitHub Issues: https://github.com/your-org/vibe-note/issues
- 文件問題：查看 `specs/` 目錄

---

**由 Claude Code 與 Spec Kit 驅動** 🚀
