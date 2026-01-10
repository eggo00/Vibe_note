# Implementation Plan: Vibe Coding AI 學霸筆記生成器

**Branch**: `001-ai-note-generator` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-note-generator/spec.md`

## Summary

開發一個 AI 驅動的學習筆記自動生成系統，核心功能包含：

1. **資料爬取**：從 Notion 公開頁面、Blog/Substack、GitHub Repo 爬取內容
2. **內容分析**：對 Notion 內容進行 block-level 品質評分，僅保留高品質段落
3. **風格學習**：分析老師文章寫作風格，建立 style profile
4. **筆記生成**：基於多源資料產出結構化 Markdown 筆記草稿
5. **線上編輯**：提供 Markdown 編輯器，支援 undo/redo、版本管理、即時預覽
6. **多格式匯出**：支援 Markdown、HTML、PDF 匯出與一鍵複製

**技術方向**：採用前後端分離架構，後端 Python FastAPI 提供 RESTful API，前端 React 實作編輯器與使用者介面，資料庫使用 SQLite（MVP 階段）。

## Technical Context

**Language/Version**: Python 3.11+ (後端), TypeScript/JavaScript (前端)
**Primary Dependencies**:
- 後端：FastAPI, Pydantic, Beautiful Soup 4, Playwright, SQLAlchemy
- 前端：React 18, Monaco Editor (或 TipTap), Axios
- AI/NLP：OpenAI API (或本地 LLM，待研究階段確認)

**Storage**: SQLite (MVP 階段), 未來可升級為 PostgreSQL
**Testing**: 不實作自動化測試（憲章要求），提供 E2E 手動測試步驟與 Swagger API 文件
**Target Platform**: Web 應用，支援現代瀏覽器（Chrome, Firefox, Safari）
**Project Type**: Web 應用（前端 + 後端分離）
**Performance Goals**:
- 爬取 3 個 Notion 頁面 + 2 篇 Blog + 1 個 GitHub Repo 總時間 < 5 分鐘
- 筆記生成時間 < 2 分鐘
- 編輯器操作回應時間 < 100ms
- 版本自動儲存觸發時間 30 秒

**Constraints**:
- 爬蟲 rate limiting：每秒最多 1 次請求
- 單次處理資料來源 ≤ 10 個
- GitHub Repo 大小 ≤ 100MB，檔案數 ≤ 500 個
- Notion 頁面內容 ≤ 50MB
- 版本歷史保留最近 50 個
- 資料保留期限 30 天

**Scale/Scope**:
- MVP 階段：單使用者模式（無多人協作）
- 預期同時處理 1-3 個筆記專案
- 生成筆記長度 2000-10000 字
- 支援中文與英文混合內容

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. MVP 優先開發
- **符合性**：架構設計採用最簡單的前後端分離，避免微服務、訊息佇列等複雜架構
- **符合性**：資料庫選用 SQLite 而非 PostgreSQL，降低部署複雜度
- **符合性**：版本控制採用簡單的「完整快照」模式，不使用差異演算法
- **符合性**：優先實作 P1 功能（Notion 爬取 → 生成筆記），P2/P3 功能可逐步迭代

### ✅ II. 使用者體驗至上
- **符合性**：所有 API 錯誤回傳統一格式，前端統一處理錯誤提示
- **符合性**：爬蟲失敗時提供手動貼上內容的 fallback UI
- **符合性**：編輯器支援 undo/redo 與即時預覽，降低操作成本
- **符合性**：版本歷史列表顯示預覽前 50 字，方便快速識別
- **符合性**：localStorage 自動備份草稿，避免網路中斷資料遺失

### ✅ III. 程式碼簡潔與可維護性
- **符合性**：後端使用 FastAPI 的自動文件生成，減少手寫文件工作
- **符合性**：前端元件按功能模組劃分（Scraper, Editor, Export），職責單一
- **符合性**：避免過度抽象，直接使用 SQLAlchemy ORM 而非 Repository 模式
- **符合性**：Python 使用 type hints，TypeScript 強制型別檢查

### ✅ IV. 資料隱私與合規
- **符合性**：爬蟲前檢查 robots.txt，User-Agent 標註為 "VibeCodingNoteBot/1.0"
- **符合性**：所有資料來源記錄 URL、時間戳與原始快照
- **符合性**：實作定時任務（cron job）每日清理 30 天前的資料
- **符合性**：不儲存使用者個人身份資訊（無登入系統）
- **符合性**：爬蟲遇到 403 或登入牆時拒絕存取

### ✅ V. 容錯與優雅降級
- **符合性**：爬蟲失敗不影響其他資料來源處理（獨立錯誤處理）
- **符合性**：風格學習失敗時使用預設「教學友善風格」模板
- **符合性**：GitHub Repo 過大時僅分析 README 與主要目錄
- **符合性**：前端編輯器使用 localStorage 作為本地備份
- **符合性**：API 回傳統一錯誤格式，包含 error code 與描述

### ⚠️ 技術約束檢查
- **符合性**：不實作自動化測試，提供 Swagger 文件 + 手動測試步驟
- **符合性**：爬蟲模組實作 rate limiter（每秒最多 1 次請求）
- **符合性**：Python 後端使用 type hints，前端使用 TypeScript

### 憲章合規結論
✅ **通過**：所有設計決策符合憲章五大原則與技術約束，無需特殊理由的複雜度引入。

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-note-generator/
├── spec.md              # 功能規格（已完成）
├── plan.md              # 本檔案 - 技術實作計畫
├── research.md          # Phase 0 - 技術研究與決策
├── data-model.md        # Phase 1 - 資料模型設計
├── quickstart.md        # Phase 1 - 快速開始指南
├── contracts/           # Phase 1 - API 合約定義
│   ├── openapi.yaml     # OpenAPI 3.0 規格
│   └── examples/        # API 請求/回應範例
├── checklists/          # 品質檢查清單
│   └── requirements.md  # 規格品質檢查（已完成）
└── tasks.md             # Phase 2 - 任務拆解（/speckit.tasks 產生）
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                  # FastAPI 應用入口
│   ├── config.py                # 環境設定與常數
│   ├── models/                  # SQLAlchemy 資料模型
│   │   ├── document.py          # Document, Version 實體
│   │   ├── data_source.py       # DataSource, Block 實體
│   │   ├── style_profile.py     # StyleProfile 實體
│   │   └── export_job.py        # ExportJob 實體
│   ├── services/                # 業務邏輯層
│   │   ├── scraper/             # 爬蟲模組
│   │   │   ├── notion.py        # Notion 爬蟲
│   │   │   ├── blog.py          # Blog/Substack 爬蟲
│   │   │   ├── github.py        # GitHub Repo 爬蟲
│   │   │   └── rate_limiter.py  # Rate limiting 實作
│   │   ├── analyzer/            # 內容分析模組
│   │   │   ├── quality_scorer.py  # Block-level 品質評分
│   │   │   └── style_learner.py   # 風格學習與建模
│   │   ├── generator/           # 筆記生成模組
│   │   │   └── note_generator.py  # Markdown 筆記生成器
│   │   ├── editor/              # 編輯與版本控制
│   │   │   └── version_manager.py  # 版本管理邏輯
│   │   └── exporter/            # 匯出模組
│   │       ├── markdown.py      # Markdown 匯出
│   │       ├── html.py          # HTML 匯出
│   │       └── pdf.py           # PDF 匯出（Puppeteer）
│   ├── api/                     # API 路由層
│   │   ├── notion.py            # POST /api/notion/import
│   │   ├── blog.py              # POST /api/blog/import
│   │   ├── analyze.py           # POST /api/analyze
│   │   ├── style.py             # POST /api/style/build
│   │   ├── generate.py          # POST /api/generate
│   │   ├── documents.py         # GET/PUT /api/doc/{id}
│   │   └── export.py            # POST /api/doc/{id}/export
│   ├── schemas/                 # Pydantic schemas (request/response)
│   │   ├── scraper.py           # 爬蟲相關 schemas
│   │   ├── document.py          # 文件相關 schemas
│   │   └── common.py            # 共用 schemas (錯誤格式等)
│   └── utils/                   # 工具函式
│       ├── db.py                # 資料庫連線與初始化
│       ├── text_similarity.py   # 文字相似度計算（防抄襲）
│       └── cleanup.py           # 定時清理 30 天資料
├── tests/                       # （MVP 不實作）
├── migrations/                  # 資料庫 migration（若需要）
├── requirements.txt             # Python 依賴
├── .env.example                 # 環境變數範例
└── README.md                    # 後端說明文件

frontend/
├── src/
│   ├── App.tsx                  # React 應用入口
│   ├── pages/                   # 頁面元件
│   │   ├── HomePage.tsx         # 首頁：輸入資料來源
│   │   ├── EditorPage.tsx       # 編輯器頁面
│   │   └── NotFoundPage.tsx     # 404 頁面
│   ├── components/              # 可重用元件
│   │   ├── Scraper/             # 爬蟲相關元件
│   │   │   ├── DataSourceInput.tsx    # 資料來源輸入表單
│   │   │   ├── ScraperProgress.tsx    # 爬取進度顯示
│   │   │   └── ManualInputModal.tsx   # 手動貼上內容 Modal
│   │   ├── Editor/              # 編輯器相關元件
│   │   │   ├── MarkdownEditor.tsx     # Monaco/TipTap 編輯器
│   │   │   ├── PreviewPanel.tsx       # Markdown 預覽面板
│   │   │   ├── VersionHistory.tsx     # 版本歷史列表
│   │   │   └── Toolbar.tsx            # 編輯器工具列（undo/redo/save）
│   │   ├── Export/              # 匯出相關元件
│   │   │   ├── ExportButtons.tsx      # 匯出按鈕組
│   │   │   └── CopyToClipboard.tsx    # 一鍵複製按鈕
│   │   └── Common/              # 共用元件
│   │       ├── ErrorMessage.tsx       # 錯誤訊息顯示
│   │       ├── LoadingSpinner.tsx     # 載入動畫
│   │       └── Button.tsx             # 通用按鈕元件
│   ├── services/                # API 呼叫與業務邏輯
│   │   ├── api.ts               # Axios 設定與攔截器
│   │   ├── scraperService.ts    # 爬蟲 API 呼叫
│   │   ├── documentService.ts   # 文件 API 呼叫
│   │   ├── exportService.ts     # 匯出 API 呼叫
│   │   └── localStorageService.ts  # localStorage 備份邏輯
│   ├── types/                   # TypeScript 型別定義
│   │   ├── document.ts          # Document, Version 型別
│   │   ├── dataSource.ts        # DataSource, Block 型別
│   │   └── api.ts               # API 請求/回應型別
│   ├── hooks/                   # React Hooks
│   │   ├── useEditor.ts         # 編輯器狀態管理（undo/redo）
│   │   ├── useAutoSave.ts       # 自動儲存 Hook
│   │   └── useLocalBackup.ts    # localStorage 備份 Hook
│   ├── styles/                  # CSS/SCSS 樣式
│   │   ├── global.css           # 全域樣式
│   │   └── editor.css           # 編輯器專用樣式
│   └── utils/                   # 前端工具函式
│       ├── markdown.ts          # Markdown 解析與渲染
│       └── clipboard.ts         # 剪貼簿操作
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
├── .env.example
└── README.md

shared/                          # 前後端共用（若需要）
└── types/                       # 共用型別定義（可選）

docs/                            # 專案文件
├── api-manual-tests.md          # API 手動測試步驟
├── e2e-test-scenarios.md        # E2E 測試情境
└── deployment.md                # 部署指南

scripts/                         # 工具腳本
├── cleanup_old_data.py          # 清理 30 天資料的 cron job
└── init_db.py                   # 資料庫初始化腳本

.gitignore
docker-compose.yml               # Docker 本地開發環境
README.md                        # 專案整體說明
```

**Structure Decision**: 選擇 **Option 2: Web application** 架構，理由如下：

1. **前後端分離**：前端專注於編輯器 UX，後端專注於爬蟲與分析邏輯，職責清晰
2. **獨立部署**：前端可部署到 CDN，後端部署到 Server，提升效能與擴展性
3. **技術棧自由**：前端使用 TypeScript/React，後端使用 Python，各自發揮語言優勢
4. **MVP 友善**：兩個獨立專案比單體應用更容易理解與維護，符合憲章簡潔原則

## Complexity Tracking

> **本節為空**：所有設計決策均符合憲章要求，無需特殊理由的複雜度引入。

---

## Phase 0: Research & Decisions

### 待研究項目

以下技術選擇需要在 Phase 0 研究階段確認：

1. **AI/NLP 模型選擇**
   - 選項 A：OpenAI API (GPT-4 或 GPT-3.5)
   - 選項 B：本地 LLM (Llama 2, Mistral)
   - 選項 C：混合方案（品質評分用本地，風格學習用 API）
   - **需評估**：成本、效能、離線可用性

2. **Markdown 編輯器選擇**
   - 選項 A：Monaco Editor（VS Code 核心，功能強大）
   - 選項 B：TipTap（基於 ProseMirror，更輕量）
   - **需評估**：Bundle 大小、自訂能力、undo/redo 實作難度

3. **PDF 匯出實作方式**
   - 選項 A：Puppeteer（渲染 HTML → PDF）
   - 選項 B：wkhtmltopdf（命令列工具）
   - 選項 C：前端 jsPDF（純客戶端，無需後端）
   - **需評估**：部署複雜度、排版品質、中文支援

4. **爬蟲方案選擇**
   - Notion: 選項 A：官方 Notion API, 選項 B：HTML 解析
   - Blog: 選項 A：Beautiful Soup, 選項 B：Playwright（處理 JS 渲染）
   - GitHub: 選項 A：GitHub API, 選項 B：直接爬取 raw.githubusercontent.com
   - **需評估**：穩定性、API 限制、robots.txt 合規性

5. **文字相似度演算法**
   - 用途：驗證生成內容不含直接複製的原文句子
   - 選項 A：Cosine Similarity + TF-IDF
   - 選項 B：Levenshtein Distance
   - 選項 C：第三方 API（如 CopyScape）
   - **需評估**：準確度、效能、實作複雜度

6. **版本儲存策略**
   - 選項 A：完整快照（每個版本儲存完整 content）
   - 選項 B：差異儲存（儲存 diff，節省空間）
   - **建議**：選擇 A（完整快照），符合 MVP 簡潔原則

### 研究輸出

Phase 0 將產生 `research.md`，包含以上所有決策的：
- **最終選擇**
- **理由與權衡**
- **替代方案評估**
- **實作建議**

---

## Phase 1: Design & Contracts

### 1.1 資料模型設計 (data-model.md)

將規格中的 Key Entities 轉換為具體資料表設計：

- **Document**：筆記文件主表
- **Version**：版本歷史表
- **DataSource**：資料來源表
- **Block**：Notion block 內容表
- **StyleProfile**：風格模型表
- **ExportJob**：匯出任務表

包含欄位定義、關聯關係、索引設計、資料驗證規則。

### 1.2 API 合約設計 (contracts/openapi.yaml)

根據規格 FR-033 到 FR-044，產生完整的 OpenAPI 3.0 規格：

```yaml
openapi: 3.0.0
info:
  title: Vibe Note API
  version: 1.0.0
paths:
  /api/notion/import:
    post: ...
  /api/blog/import:
    post: ...
  /api/analyze:
    post: ...
  /api/style/build:
    post: ...
  /api/generate:
    post: ...
  /api/doc/{id}:
    get: ...
    put: ...
  /api/doc/{id}/restore:
    post: ...
  /api/doc/{id}/export:
    post: ...
```

包含每個端點的：
- 請求參數與 body schemas
- 回應格式（成功與錯誤）
- 範例 request/response
- 錯誤碼定義（ERROR_CODE）

### 1.3 快速開始指南 (quickstart.md)

提供開發者快速啟動專案的步驟：

1. **環境需求**：Python 3.11+, Node.js 18+, Docker (可選)
2. **後端啟動**：
   ```bash
   cd backend
   pip install -r requirements.txt
   python src/main.py
   ```
3. **前端啟動**：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. **存取 API 文件**：http://localhost:8000/docs (Swagger UI)
5. **手動測試流程**：參考 `docs/api-manual-tests.md`

### 1.4 Agent Context 更新

Phase 1 完成後，執行：

```bash
bash .specify/scripts/bash/update-agent-context.sh claude
```

將以下技術資訊更新到 `.claude/` 目錄：
- 技術棧：Python FastAPI, React, TypeScript, SQLite
- 專案結構：前後端分離架構
- API 設計：RESTful, OpenAPI 3.0
- 關鍵決策：來自 research.md 的最終選擇

---

## Next Steps

Phase 1 完成後，執行以下命令繼續：

```bash
# 產生任務清單
/speckit.tasks

# 或產生品質檢查清單（可選）
/speckit.checklist
```

任務清單將根據本計畫的 Phase 0 和 Phase 1 設計，拆解為可執行的開發任務，按優先級排序（P1 核心功能優先）。
