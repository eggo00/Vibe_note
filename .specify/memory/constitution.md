<!--
Sync Impact Report
==================
Version change: INITIAL → 1.0.0
Modified principles: N/A (initial creation)
Added sections:
  - Core Principles (5 principles)
  - Technical Constraints
  - Development Workflow
  - Governance
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (will align with MVP-first approach)
  ✅ .specify/templates/spec-template.md (will align with data privacy requirements)
  ✅ .specify/templates/tasks-template.md (will reflect no testing requirement)
Follow-up TODOs: None
-->

# Vibe Note 專案憲章

## 核心原則

### I. MVP 優先開發
所有功能開發必須以「最小可行產品」為目標。每個 feature 必須：
- 優先實作核心功能，避免過度設計
- 可以在後續迭代中優化，而非一次做到完美
- 快速驗證可行性，再決定是否深入開發
- 遵循 YAGNI 原則（You Aren't Gonna Need It）

**理由**：快速交付價值，避免浪費時間在不確定的需求上。

### II. 使用者體驗至上
產品設計必須以使用者需求為中心：
- UI/UX 必須直觀易用，減少學習成本
- 提供即時反饋與錯誤提示
- 支援 undo/redo 等常見操作習慣
- 所有匯出格式必須符合實際繳交需求
- 當爬蟲失敗時，必須提供友善的 fallback（例如手動貼上）

**理由**：這是給學生用的工具，必須降低使用門檻，讓學習者專注在內容而非工具本身。

### III. 程式碼簡潔與可維護性
程式碼必須保持簡單、清晰、可讀：
- 避免過度抽象與不必要的設計模式
- 函式與模組職責單一明確
- 變數與函式命名具有描述性
- 重複程式碼在第三次出現時才考慮抽象化
- 註解說明「為什麼」而非「做什麼」

**理由**：MVP 階段需求變動頻繁，簡潔的程式碼更容易修改與重構。

### IV. 資料隱私與合規
系統必須尊重資料來源與使用者隱私：
- 嚴禁繞過付費牆或需登入的內容
- 遵守 robots.txt 規範
- 明確記錄所有資料來源與爬取時間
- 使用者資料預設保留 30 天後自動刪除
- 不得儲存或傳輸任何敏感個人資訊
- 所有爬取行為必須標註 User-Agent

**理由**：尊重智慧財產權與隱私法規，避免法律風險，建立可信賴的產品。

### V. 容錯與優雅降級
系統在遇到錯誤時必須優雅處理：
- 爬蟲失敗時提供手動輸入選項
- API 錯誤必須回傳清楚的錯誤訊息
- 自動儲存功能避免使用者資料遺失
- 不可因單一模組失敗導致整個系統崩潰
- 提供合理的預設值與備用方案

**理由**：提升系統穩定性與使用者體驗，減少挫折感。

## 技術約束

### 選擇性測試策略
本專案採用「關鍵 function 寫測試」的折衷方案：

**必須撰寫測試的模組**：
- 爬蟲模組（Notion, Blog, GitHub scraper）
- 內容分析與品質評分器
- 筆記生成器（核心 AI 邏輯）
- 文字相似度檢查
- 版本控制邏輯

**可使用手動測試的模組**：
- API 端點（使用 FastAPI Swagger UI 測試）
- 前端 UI 元件（使用瀏覽器手動測試）
- 資料庫 CRUD 操作（使用 SQLAlchemy 的型別安全）

**測試規範**：
- 使用 pytest 作為測試框架
- 每個關鍵 function 至少覆蓋正常情境 + 1-2 個異常情境
- 所有 Python 程式碼必須使用 type hints
- TypeScript 必須啟用 strict 模式

**理由**：平衡開發效率與程式碼品質，將測試資源集中在最容易出錯且影響最大的核心邏輯。

### 資料處理
- 所有爬蟲必須尊重 rate limiting（預設每秒最多 1 次請求）
- 內容分析必須在 block-level 進行，而非整篇文章
- 不得直接複製原文句子，僅學習風格與結構
- 資料來源必須可追溯（記錄 URL、爬取時間、版本）

### 技術棧選擇
- 後端：Python（FastAPI 或 Flask）
- 前端：現代 JS 框架（React / Vue / Next.js）
- 資料庫：SQLite（MVP）或 PostgreSQL（生產環境）
- 爬蟲：Beautiful Soup / Playwright
- 編輯器：Monaco Editor 或 TipTap

### 套件管理規範
- **Python 套件管理**：本專案統一使用 **UV** 進行套件管理與虛擬環境建立
  - 建立虛擬環境：`uv venv`
  - 安裝依賴：`uv pip install -r requirements.txt`
  - 新增套件：`uv pip install <package>`
- **Node.js 套件管理**：前端使用 npm 或其他 Node.js 套件管理工具
- **理由**：UV 提供更快的套件解析與安裝速度，統一工具鏈可減少環境配置問題

## 開發流程

### MVP 迭代原則
1. 先實作核心 API（爬蟲 → 分析 → 生成 → 編輯）
2. 再實作基本 UI（可以是命令列或簡易網頁）
3. 最後優化體驗（版本控制、匯出、美化）

### API 設計規範
- 使用 RESTful 原則
- 所有 API 必須提供 OpenAPI/Swagger 文件
- 錯誤訊息使用統一格式：`{"error": "描述", "code": "ERROR_CODE"}`
- 成功回應使用統一格式：`{"success": true, "data": {...}}`

### 版本控制
- 使用 Git 進行版本控制
- Commit message 使用中文，清楚描述改動內容
- 功能開發在獨立分支，完成後合併回 main

### 敏感資訊保護
**禁止上傳到 GitHub 的敏感檔案**：
- 環境變數檔案（`.env`, `.env.local`, `.env.production`）
- API 金鑰與憑證（OpenAI API key, database credentials）
- 資料庫檔案（`*.db`, `*.sqlite`, `*.sqlite3`）
- 私鑰與憑證（`*.pem`, `*.key`, `*.crt`）
- 使用者上傳的檔案與匯出結果

**強制措施**：
- `.gitignore` 必須包含所有敏感檔案模式
- 提供 `.env.example` 作為環境變數範本（不含實際值）
- 使用環境變數而非硬編碼儲存敏感資訊
- Code review 時檢查是否有 hardcoded secrets

**理由**：避免憑證洩漏導致安全風險與費用損失

## 治理規範

### 憲章地位
本憲章定義專案的核心價值與開發原則。所有設計決策與程式碼審查必須符合本憲章。

### 修訂程序
憲章修訂需要：
1. 明確記錄修改原因與影響範圍
2. 更新版本號（語意化版本）
3. 同步更新相關模板與文件
4. 在 Git 中留下清楚的 commit 記錄

### 版本號規則
- MAJOR：移除或重新定義核心原則
- MINOR：新增原則或重大擴充
- PATCH：澄清說明、修正錯字、非語意調整

### 複雜度管理
任何增加系統複雜度的提案（新增抽象層、設計模式、第三方服務）必須提供明確理由，並證明其必要性。

**Version**: 1.1.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-08

## 變更歷史

### v1.1.0 (2026-01-08)
- **MINOR**: 修改測試策略，從「不實作自動化測試」改為「選擇性測試策略」
- **MINOR**: 新增「套件管理規範」章節，規定使用 UV 進行 Python 套件管理
- 理由：在開發過程中發現核心業務邏輯（爬蟲、分析、生成）需要測試保護，採用折衷方案平衡效率與品質
