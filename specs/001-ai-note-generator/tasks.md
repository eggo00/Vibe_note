# Implementation Tasks: Vibe Coding AI 學霸筆記生成器

**Feature Branch**: `001-ai-note-generator`
**Created**: 2026-01-07
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

本任務清單按照 User Story 優先級組織，每個 Story 可獨立實作與驗證。

**總任務數**: 78 tasks
**MVP 範圍**: Phase 3 (User Story 1) - 完成核心筆記生成功能
**預估時程**: MVP 2-3 週，完整功能 4-6 週

---

## Task Execution Strategy

### MVP First Approach (憲章原則)
1. **Phase 1-2**: 建立基礎架構（1-2 天）
2. **Phase 3 (US1)**: 實作核心功能（1-1.5 週）- **MVP 交付點**
3. **Phase 4-6 (US2-4)**: 增量迭代（各 3-5 天）
4. **Phase 7 (US5)**: 增強功能（2-3 天）
5. **Phase 8**: 打磨與優化（2-3 天）

### Parallel Execution Opportunities
- **Setup 階段**: T001-T006 可並行執行
- **Foundational 階段**: T007-T015 中，T008-T014 可並行（不同檔案）
- **每個 User Story 內**: 標註 [P] 的任務可並行（同一 Story 內的獨立檔案）

### Independent Test Criteria
每個 User Story 結束時都有明確的驗收標準（見各 Phase 的 Story Goal）

---

## Phase 1: Setup & Infrastructure (環境建置)

**Goal**: 建立專案基礎結構與開發環境

- [ ] T001 建立專案根目錄結構（backend/, frontend/, docs/, scripts/）
- [ ] T002 [P] 初始化後端專案（建立 backend/src/ 結構，參考 plan.md §Project Structure）
- [ ] T003 [P] 初始化前端專案（建立 frontend/src/ 結構，參考 plan.md §Project Structure）
- [ ] T004 [P] 建立 backend/requirements.txt（依據 research.md 技術選型）
- [ ] T005 [P] 建立 frontend/package.json（React 18 + TypeScript + Monaco Editor）
- [ ] T006 [P] 建立環境變數範例檔案（backend/.env.example, frontend/.env.example，參考 quickstart.md）
- [ ] T007 建立 scripts/init_db.py（執行 data-model.md 的 SQL 初始化腳本）
- [ ] T008 [P] 建立 docker-compose.yml（包含後端、前端服務定義）
- [ ] T009 [P] 建立 .gitignore（排除 .env, venv/, node_modules/, *.db）
- [ ] T010 建立 README.md（專案說明、快速啟動、技術棧，參考 quickstart.md）

**Validation**: 執行 `docker-compose up` 成功啟動空白應用

---

## Phase 2: Foundational Components (基礎元件)

**Goal**: 實作所有 User Stories 共用的核心模組

### 資料庫層 (Backend)

- [ ] T011 實作資料庫連線模組 backend/src/utils/db.py（SQLAlchemy engine 與 session 管理）
- [ ] T012 [P] 實作 Document model in backend/src/models/document.py（對應 data-model.md §1）
- [ ] T013 [P] 實作 Version model in backend/src/models/document.py（對應 data-model.md §2）
- [ ] T014 [P] 實作 DataSource model in backend/src/models/data_source.py（對應 data-model.md §3）
- [ ] T015 [P] 實作 Block model in backend/src/models/data_source.py（對應 data-model.md §4）
- [ ] T016 [P] 實作 StyleProfile model in backend/src/models/style_profile.py（對應 data-model.md §5）
- [ ] T017 [P] 實作 ExportJob model in backend/src/models/export_job.py（對應 data-model.md §6）

### 共用工具模組 (Backend)

- [ ] T018 [P] 實作 RateLimiter in backend/src/services/scraper/rate_limiter.py（每秒 1 次請求限制，參考 research.md §4）
- [ ] T019 [P] 實作文字相似度檢查 backend/src/utils/text_similarity.py（Cosine Similarity，參考 research.md §5）
- [ ] T020 [P] 實作錯誤格式化工具 backend/src/schemas/common.py（統一錯誤回應格式，參考 spec.md §FR-042）

### API 基礎架構 (Backend)

- [ ] T021 建立 FastAPI 應用入口 backend/src/main.py（CORS 設定、路由註冊、Swagger 啟用）
- [ ] T022 建立環境設定模組 backend/src/config.py（載入 .env 變數）
- [ ] T023 實作健康檢查端點 GET /health in backend/src/api/health.py

### 前端基礎架構

- [ ] T024 [P] 建立 React App 入口 frontend/src/App.tsx（路由設定）
- [ ] T025 [P] 實作 API client 模組 frontend/src/services/api.ts（Axios 設定、統一錯誤處理）
- [ ] T026 [P] 實作錯誤訊息元件 frontend/src/components/Common/ErrorMessage.tsx
- [ ] T027 [P] 實作載入動畫元件 frontend/src/components/Common/LoadingSpinner.tsx

**Validation**:
- 後端 `python backend/src/main.py` 啟動成功，存取 http://localhost:8000/docs 顯示 Swagger UI
- 前端 `npm run dev` 啟動成功，存取 http://localhost:3000 顯示空白首頁

---

## Phase 3: User Story 1 - 從 Notion 作業生成筆記草稿 (P1) 🎯 **MVP**

**Story Goal**: 使用者輸入 Notion URL 與對話紀錄，系統爬取、分析並產出 Markdown 筆記草稿

**Independent Test**:
1. 提供有效的 Notion 公開 URL
2. 提供對話紀錄 Markdown 檔案
3. 點擊「開始分析」
4. 驗證產出的筆記包含專案摘要、程式碼範例、常見錯誤段落

**Priority**: P1 (最高優先級，MVP 核心功能)

### 後端 - Notion 爬蟲模組

- [ ] T028 [P] [US1] 實作 Notion 爬蟲 backend/src/services/scraper/notion.py（使用 BeautifulSoup 解析 HTML，參考 research.md §4）
- [ ] T029 [P] [US1] 實作 robots.txt 檢查工具 backend/src/services/scraper/notion.py（遵守爬蟲規範，參考 spec.md §FR-030）
- [ ] T030 [US1] 實作 POST /api/notion/import in backend/src/api/notion.py（呼叫 Notion 爬蟲，儲存 DataSource 與 Blocks）

### 後端 - 內容分析模組

- [ ] T031 [P] [US1] 實作 Block 品質評分器 backend/src/services/analyzer/quality_scorer.py（使用 OpenAI API 評分，參考 spec.md §FR-007）
- [ ] T032 [US1] 實作 POST /api/analyze in backend/src/api/analyze.py（呼叫評分器，過濾 score >= 60 的 blocks）

### 後端 - 筆記生成模組

- [ ] T033 [P] [US1] 實作筆記生成器 backend/src/services/generator/note_generator.py（基於對話紀錄與高品質 blocks 生成 Markdown）
- [ ] T034 [P] [US1] 實作預設風格模板 backend/src/services/generator/note_generator.py（教學友善風格，參考 spec.md §FR-013）
- [ ] T035 [US1] 實作 POST /api/generate in backend/src/api/generate.py（呼叫生成器，建立 Document 與 Version）

### 後端 - 文件管理 API

- [ ] T036 [P] [US1] 實作 GET /api/doc/{id} in backend/src/api/documents.py（回傳當前版本內容）
- [ ] T037 [P] [US1] 實作 PUT /api/doc/{id} in backend/src/api/documents.py（更新內容，建立新版本）

### 前端 - 資料輸入與進度顯示

- [ ] T038 [P] [US1] 實作首頁 frontend/src/pages/HomePage.tsx（包含資料來源輸入表單）
- [ ] T039 [P] [US1] 實作資料來源輸入元件 frontend/src/components/Scraper/DataSourceInput.tsx（Notion URL、對話紀錄檔案上傳）
- [ ] T040 [P] [US1] 實作爬取進度顯示元件 frontend/src/components/Scraper/ScraperProgress.tsx（顯示爬取狀態與進度）
- [ ] T041 [P] [US1] 實作手動貼上 Modal frontend/src/components/Scraper/ManualInputModal.tsx（爬蟲失敗的 fallback）

### 前端 - API 呼叫服務

- [ ] T042 [P] [US1] 實作爬蟲服務 frontend/src/services/scraperService.ts（呼叫 /api/notion/import, /api/analyze）
- [ ] T043 [P] [US1] 實作文件服務 frontend/src/services/documentService.ts（呼叫 /api/generate, /api/doc/{id}）

### 整合與驗證

- [ ] T044 [US1] 整合前後端：完整流程測試（輸入 → 爬取 → 分析 → 生成 → 顯示筆記）
- [ ] T045 [US1] 實作錯誤處理：爬蟲失敗、API 超時、無高品質 blocks 等情境

**Phase 3 Validation (MVP 驗收)**:
- [ ] 成功爬取 Notion 公開頁面
- [ ] Block 品質評分正確運作（score >= 60 保留）
- [ ] 生成的筆記包含專案摘要、程式碼範例、常見錯誤段落
- [ ] 錯誤情境（404、403、無內容）有友善提示

---

## Phase 4: User Story 2 - 學習老師寫作風格並應用 (P2)

**Story Goal**: 使用者提供老師 Blog URL，系統分析風格並應用到筆記生成

**Independent Test**:
1. 提供 2-3 篇老師 Blog URL
2. 系統分析產生 style_profile.json
3. 生成筆記時套用此風格
4. 驗證筆記的標題模式、段落順序與老師文章相似

**Priority**: P2

### 後端 - Blog 爬蟲與風格分析

- [ ] T046 [P] [US2] 實作 Blog 爬蟲 backend/src/services/scraper/blog.py（使用 Playwright 處理 JS 渲染，參考 research.md §4）
- [ ] T047 [US2] 實作 POST /api/blog/import in backend/src/api/blog.py（呼叫 Blog 爬蟲）
- [ ] T048 [P] [US2] 實作風格學習器 backend/src/services/analyzer/style_learner.py（分析標題模式、段落順序、語氣，參考 spec.md §FR-011）
- [ ] T049 [US2] 實作 POST /api/style/build in backend/src/api/style.py（呼叫風格學習器，儲存 StyleProfile）
- [ ] T050 [US2] 更新筆記生成器：套用 style_profile（修改 backend/src/services/generator/note_generator.py）

### 前端 - Blog 輸入與風格選擇

- [ ] T051 [P] [US2] 更新資料來源輸入元件：新增 Blog URL 輸入欄位（frontend/src/components/Scraper/DataSourceInput.tsx）
- [ ] T052 [P] [US2] 實作風格選擇元件 frontend/src/components/Scraper/StyleSelector.tsx（顯示可用風格列表）

### 整合與驗證

- [ ] T053 [US2] 整合風格學習流程：Blog 爬取 → 風格分析 → 套用到生成
- [ ] T054 [US2] 驗證風格套用效果：比對生成筆記與老師文章的結構相似度

**Phase 4 Validation**:
- [ ] 成功爬取 Blog/Substack 文章
- [ ] 風格分析識別出至少 5 個特徵（標題模式、段落順序等）
- [ ] 生成筆記套用風格後，結構與老師文章相似

---

## Phase 5: User Story 3 - 線上編輯與版本管理 (P2)

**Story Goal**: 使用者在瀏覽器中編輯筆記，支援 undo/redo、自動儲存、版本還原

**Independent Test**:
1. 開啟編輯器載入筆記
2. 修改內容，等待 30 秒自動儲存
3. 執行 undo/redo 操作
4. 查看版本歷史並還原到舊版本

**Priority**: P2

### 後端 - 版本管理 API

- [ ] T055 [P] [US3] 實作版本管理服務 backend/src/services/editor/version_manager.py（建立版本、還原版本邏輯）
- [ ] T056 [P] [US3] 實作 GET /api/doc/{id}/versions in backend/src/api/documents.py（回傳版本歷史列表）
- [ ] T057 [P] [US3] 實作 POST /api/doc/{id}/restore in backend/src/api/documents.py（還原到指定版本）

### 前端 - Markdown 編輯器

- [ ] T058 [P] [US3] 實作編輯器頁面 frontend/src/pages/EditorPage.tsx
- [ ] T059 [P] [US3] 整合 Monaco Editor frontend/src/components/Editor/MarkdownEditor.tsx（Markdown 模式、語法高亮）
- [ ] T060 [P] [US3] 實作預覽面板 frontend/src/components/Editor/PreviewPanel.tsx（即時渲染 Markdown）
- [ ] T061 [P] [US3] 實作編輯器工具列 frontend/src/components/Editor/Toolbar.tsx（undo/redo/save 按鈕）

### 前端 - 版本控制

- [ ] T062 [P] [US3] 實作版本歷史元件 frontend/src/components/Editor/VersionHistory.tsx（顯示版本列表、預覽前 50 字）
- [ ] T063 [P] [US3] 實作編輯器狀態管理 Hook frontend/src/hooks/useEditor.ts（undo/redo stack 管理）
- [ ] T064 [P] [US3] 實作自動儲存 Hook frontend/src/hooks/useAutoSave.ts（debounce 30 秒）
- [ ] T065 [P] [US3] 實作 localStorage 備份 Hook frontend/src/hooks/useLocalBackup.ts（網路中斷時保存草稿）

### 整合與驗證

- [ ] T066 [US3] 整合編輯器與版本管理：完整編輯流程測試
- [ ] T067 [US3] 驗證 undo/redo 功能：執行 20+ 次操作並正確還原
- [ ] T068 [US3] 驗證自動儲存：修改內容後 30 秒自動建立新版本
- [ ] T069 [US3] 驗證 localStorage 備份：關閉瀏覽器後重新開啟能還原草稿

**Phase 5 Validation**:
- [ ] 編輯器正確顯示 Markdown 語法高亮與即時預覽
- [ ] Undo/redo 在 100 次操作內正確運作
- [ ] 自動儲存每 30 秒觸發一次
- [ ] 版本歷史列表正確顯示，還原功能正常

---

## Phase 6: User Story 4 - 匯出多種格式繳交作業 (P2)

**Story Goal**: 使用者將筆記匯出為 Markdown/HTML/PDF，或一鍵複製到剪貼簿

**Independent Test**:
1. 完成筆記編輯
2. 點擊「匯出 PDF」
3. 驗證下載的 PDF 檔案排版正確、程式碼高亮
4. 點擊「一鍵複製」，驗證剪貼簿內容正確

**Priority**: P2

### 後端 - 匯出模組

- [ ] T070 [P] [US4] 實作 Markdown 匯出 backend/src/services/exporter/markdown.py（直接回傳內容）
- [ ] T071 [P] [US4] 實作 HTML 匯出 backend/src/services/exporter/html.py（使用 marked + highlight.js 轉換）
- [ ] T072 [P] [US4] 實作 PDF 匯出 backend/src/services/exporter/pdf.py（使用 Puppeteer 渲染，參考 research.md §3）
- [ ] T073 [US4] 實作 POST /api/doc/{id}/export in backend/src/api/export.py（根據 format 參數呼叫對應匯出器）

### 前端 - 匯出功能

- [ ] T074 [P] [US4] 實作匯出按鈕組 frontend/src/components/Export/ExportButtons.tsx（Markdown/HTML/PDF 選項）
- [ ] T075 [P] [US4] 實作一鍵複製按鈕 frontend/src/components/Export/CopyToClipboard.tsx（複製 Markdown 到剪貼簿）
- [ ] T076 [P] [US4] 實作匯出服務 frontend/src/services/exportService.ts（呼叫 /api/doc/{id}/export）

### 整合與驗證

- [ ] T077 [US4] 驗證 Markdown 匯出：檔案內容與編輯器一致
- [ ] T078 [US4] 驗證 HTML 匯出：樣式美觀、程式碼高亮正確
- [ ] T079 [US4] 驗證 PDF 匯出：排版清晰、適合列印、中文正常顯示
- [ ] T080 [US4] 驗證一鍵複製：剪貼簿內容完整

**Phase 6 Validation**:
- [ ] 所有格式匯出成功且內容完整
- [ ] PDF 排版符合 A4 規格、邊距正確
- [ ] 一鍵複製功能正常，顯示「已複製」提示

---

## Phase 7: User Story 5 - 從 GitHub Repo 提取專案資訊 (P3)

**Story Goal**: 使用者提供 GitHub Repo URL，系統讀取 README 與程式碼，整合到筆記

**Independent Test**:
1. 提供有效的 GitHub Repo URL
2. 系統爬取 README 與主要檔案
3. 生成筆記時包含「專案結構」段落
4. 驗證筆記中說明了目錄組織與關鍵檔案

**Priority**: P3

### 後端 - GitHub 爬蟲

- [ ] T081 [P] [US5] 實作 GitHub API 爬蟲 backend/src/services/scraper/github.py（使用 GitHub API 讀取檔案，參考 research.md §4）
- [ ] T082 [US5] 實作 GET /api/github/import（新增端點，或擴充 /api/notion/import 支援 GitHub URL）
- [ ] T083 [US5] 更新筆記生成器：整合 GitHub Repo 資訊（修改 backend/src/services/generator/note_generator.py）

### 前端 - GitHub 輸入

- [ ] T084 [P] [US5] 更新資料來源輸入元件：新增 GitHub Repo URL 欄位（frontend/src/components/Scraper/DataSourceInput.tsx）

### 整合與驗證

- [ ] T085 [US5] 驗證 GitHub 爬取：成功讀取 README 與主要檔案（最多 50 個）
- [ ] T086 [US5] 驗證專案結構段落：筆記包含目錄組織與關鍵檔案說明
- [ ] T087 [US5] 驗證大型 Repo 處理：超過 100MB 僅讀取 README

**Phase 7 Validation**:
- [ ] 成功爬取 GitHub Repo（公開 Repo）
- [ ] 生成筆記包含「專案結構」段落
- [ ] Repo 過大時僅分析 README，不影響整體流程

---

## Phase 8: Polish & Cross-Cutting Concerns (打磨與優化)

**Goal**: 完善系統的非功能需求與使用者體驗

### 資料清理與維護

- [ ] T088 [P] 實作資料清理腳本 scripts/cleanup_old_data.py（刪除 30 天前資料，參考 data-model.md §資料保留政策）
- [ ] T089 [P] 設定 cron job 定時執行清理腳本（每日凌晨 2:00）

### 錯誤處理與日誌

- [ ] T090 [P] 實作統一錯誤處理中介層 backend/src/middleware/error_handler.py
- [ ] T091 [P] 實作日誌記錄 backend/src/utils/logger.py（記錄 API 請求、錯誤、爬蟲狀態）

### 前端體驗優化

- [ ] T092 [P] 實作載入骨架屏 frontend/src/components/Common/Skeleton.tsx（提升載入體驗）
- [ ] T093 [P] 實作 Toast 通知元件 frontend/src/components/Common/Toast.tsx（成功/錯誤提示）
- [ ] T094 [P] 優化 RWD 響應式佈局（確保手機端可用）

### 安全性強化

- [ ] T095 [P] 實作 XSS 防護：Markdown 渲染時過濾危險標籤（frontend）
- [ ] T096 [P] 實作 rate limiting 中介層（防止 API 濫用）
- [ ] T097 [P] 實作 CORS 白名單設定（backend/src/main.py）

### 文件與部署

- [ ] T098 [P] 編寫 API 手動測試步驟文件 docs/api-manual-tests.md（參考 quickstart.md）
- [ ] T099 [P] 編寫 E2E 測試情境文件 docs/e2e-test-scenarios.md
- [ ] T100 [P] 編寫部署指南 docs/deployment.md（Docker 部署、環境變數設定）
- [ ] T101 更新專案 README.md（新增完整功能列表、架構圖、授權資訊）

**Phase 8 Validation**:
- [ ] 所有錯誤情境有友善提示
- [ ] 資料清理腳本正確執行
- [ ] 前端在各裝置上正常顯示
- [ ] 部署文件完整，可依文件成功部署

---

## Dependencies & Execution Order

### Story Dependency Graph

```
Setup (Phase 1)
  ↓
Foundational (Phase 2)
  ↓
├─→ US1 (Phase 3) - MVP ← 最優先，獨立可交付
├─→ US2 (Phase 4) - 依賴 US1 的筆記生成器
├─→ US3 (Phase 5) - 依賴 US1 的文件 API
├─→ US4 (Phase 6) - 依賴 US3 的編輯器完成
└─→ US5 (Phase 7) - 依賴 US1 的筆記生成器
  ↓
Polish (Phase 8)
```

### Story Independence

- **US1 (P1)**: 完全獨立，MVP 可單獨交付
- **US2 (P2)**: 弱依賴 US1（需要生成器），但可獨立驗證
- **US3 (P2)**: 弱依賴 US1（需要文件 API），但可獨立驗證
- **US4 (P2)**: 依賴 US3（需要編輯完成的內容）
- **US5 (P3)**: 弱依賴 US1（需要生成器），但可獨立驗證

### Parallel Execution Example (MVP - Phase 3)

**Iteration 1** (可並行):
```
T028 (Notion 爬蟲) || T031 (品質評分器) || T033 (筆記生成器) || T038 (首頁)
```

**Iteration 2** (依賴 Iteration 1):
```
T030 (Notion API) → T032 (分析 API) → T035 (生成 API)
```

**Iteration 3** (整合):
```
T044 (整合測試) → T045 (錯誤處理)
```

---

## MVP Delivery Checklist

完成 Phase 1-3 即可交付 MVP（核心筆記生成功能）：

- [ ] 使用者可輸入 Notion URL 與對話紀錄
- [ ] 系統爬取 Notion 頁面並進行 block-level 評分
- [ ] 系統生成包含專案摘要、程式碼解說、常見錯誤的 Markdown 筆記
- [ ] 爬蟲失敗時顯示友善錯誤訊息並提供手動貼上選項
- [ ] 生成的筆記可正常顯示與瀏覽

**MVP 預估時程**:
- Phase 1: 1 天
- Phase 2: 1-2 天
- Phase 3: 5-7 天
- **總計**: 7-10 天（1-1.5 週）

---

## Incremental Delivery Plan

### Week 1-2: MVP (Phase 1-3)
交付核心功能：Notion 爬取 → 分析 → 生成筆記

### Week 3: Enhancement (Phase 4-5)
新增風格學習與編輯器功能

### Week 4: Complete Features (Phase 6-7)
新增匯出與 GitHub 整合

### Week 5: Polish (Phase 8)
打磨體驗、優化效能、完善文件

---

## Task Format Validation

✅ 所有任務符合 checklist 格式：
- Checkbox: `- [ ]`
- Task ID: `T001` - `T101` (連續編號)
- [P] marker: 標註可並行任務
- [Story] label: User Story 階段任務標註 `[US1]` - `[US5]`
- Description: 清楚描述動作與檔案路徑

✅ 任務組織符合需求：
- Phase 1: Setup (10 tasks)
- Phase 2: Foundational (17 tasks)
- Phase 3: US1 - MVP (18 tasks)
- Phase 4: US2 (9 tasks)
- Phase 5: US3 (15 tasks)
- Phase 6: US4 (11 tasks)
- Phase 7: US5 (7 tasks)
- Phase 8: Polish (14 tasks)

**總計**: 101 tasks

---

## Notes

- **不寫測試**: 遵循憲章要求，MVP 階段不實作自動化測試
- **手動驗證**: 每個 Phase 結束時依照 Validation 檢查清單手動測試
- **E2E 文件**: Phase 8 會產出完整的手動測試步驟文件
- **可並行任務**: 標註 [P] 的任務可同時進行（不同檔案或獨立模組）
- **Story 獨立性**: 每個 User Story 都可獨立實作與驗證，支援增量交付

**下一步**: 開始執行 Phase 1 建立專案結構 🚀
