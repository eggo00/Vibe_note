# Feature Specification: Vibe Coding AI 學霸筆記生成器

**Feature Branch**: `001-ai-note-generator`
**Created**: 2026-01-07
**Status**: Draft
**Input**: User description: "開發 Vibe Coding 開發學霸圖文筆記撰寫 App，具備爬蟲、內容分析、風格學習、筆記生成與線上編輯功能"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 從 Notion 作業生成筆記草稿 (Priority: P1)

學生提供專案的對話紀錄 Markdown 檔、GitHub Repo URL 和多個學生優秀作業的 Notion 公開連結，系統自動爬取、分析品質、萃取高品質段落，並產出一份初步的圖文開發筆記草稿。

**Why this priority**: 這是系統的核心價值 - 自動產出筆記草稿，解決「不記筆記導致整理成本高」的問題。沒有這個功能，產品就不存在。

**Independent Test**: 可以透過提供一個 Notion 連結和對話紀錄檔案，驗證系統能否成功爬取、分析並產出可讀的 Markdown 筆記草稿。

**Acceptance Scenarios**:

1. **Given** 使用者在首頁輸入專案對話紀錄 MD 檔路徑、GitHub Repo URL 和 3 個 Notion 公開作業連結，**When** 點擊「開始分析」按鈕，**Then** 系統顯示「正在爬取資料」進度提示
2. **Given** 系統完成 Notion 內容爬取，**When** 進行 block-level 品質評分，**Then** 系統僅保留評分高於 60 分的 blocks
3. **Given** 系統已評分完成，**When** 執行筆記生成，**Then** 產出包含專案摘要、關鍵程式碼與解說的 Markdown 草稿
4. **Given** 筆記草稿已生成，**When** 使用者檢視內容，**Then** 草稿包含結構化段落（專案摘要、流程步驟、程式碼範例、常見錯誤）
5. **Given** Notion 連結無法存取，**When** 爬蟲失敗，**Then** 系統顯示友善錯誤訊息並提供「手動貼上內容」選項

---

### User Story 2 - 學習老師寫作風格並應用 (Priority: P2)

使用者提供老師的 Blog 或 Substack 公開文章連結，系統分析文章風格（段落順序、標題模式、語氣、教學句型），建立風格模型，並將此風格應用到筆記生成中。

**Why this priority**: 風格學習讓筆記更符合繳交標準，提升作業品質，但不是 MVP 的絕對必要功能（可以先用通用風格）。

**Independent Test**: 提供 2-3 篇老師 Blog 文章，驗證系統能否分析出風格特徵（如常用標題、段落節奏），並在生成筆記時反映這些特徵。

**Acceptance Scenarios**:

1. **Given** 使用者輸入老師的 Blog/Substack URL，**When** 系統爬取文章，**Then** 成功擷取標題、段落、程式碼區塊並儲存為結構化資料
2. **Given** 系統已爬取多篇文章，**When** 執行風格分析，**Then** 產生 style_profile.json，包含常見段落順序、標題模式、教學句型、語氣特徵
3. **Given** 風格模型已建立，**When** 生成筆記時套用風格，**Then** 筆記的段落順序、標題風格與老師文章相似
4. **Given** 文章需要登入或訂閱，**When** 爬蟲失敗，**Then** 系統提示「此內容需要權限」並提供手動貼上選項

---

### User Story 3 - 線上編輯與版本管理 (Priority: P2)

使用者在瀏覽器中直接編輯生成的筆記草稿，支援 undo/redo、自動儲存版本、還原到任一歷史版本，並即時預覽 Markdown 效果。

**Why this priority**: 編輯功能讓使用者能調整生成內容，版本控制避免誤刪或需要回溯，是實用性的關鍵。

**Independent Test**: 開啟編輯器、修改筆記內容、執行 undo、切換版本，驗證所有操作正確運作且資料不遺失。

**Acceptance Scenarios**:

1. **Given** 筆記草稿已載入編輯器，**When** 使用者修改任何段落，**Then** 系統每 30 秒自動儲存一次版本
2. **Given** 使用者進行了 5 次編輯，**When** 點擊「undo」按鈕，**Then** 內容回到上一步狀態
3. **Given** 使用者繼續編輯後點擊「redo」，**When** 系統執行，**Then** 內容恢復到 undo 前的狀態
4. **Given** 編輯器右側顯示版本歷史列表，**When** 使用者點選任一舊版本，**Then** 編輯器載入該版本內容並標示「歷史版本」
5. **Given** 載入歷史版本後，**When** 使用者點擊「還原此版本」，**Then** 該版本成為最新版本並可繼續編輯
6. **Given** 編輯器支援 Markdown 即時預覽，**When** 使用者輸入 Markdown 語法（如 # 標題、```程式碼```），**Then** 右側預覽窗格即時顯示渲染結果

---

### User Story 4 - 匯出多種格式繳交作業 (Priority: P2)

使用者完成編輯後，可以將筆記匯出為 Markdown、HTML 或 PDF 格式，或使用「一鍵複製繳交版」功能快速複製到剪貼簿。

**Why this priority**: 匯出功能是最終交付的必要環節，但在 MVP 階段可以先只支援 Markdown 複製。

**Independent Test**: 編輯完筆記後，點擊匯出按鈕，驗證產生的檔案格式正確且內容完整。

**Acceptance Scenarios**:

1. **Given** 使用者完成筆記編輯，**When** 點擊「匯出 Markdown」按鈕，**Then** 系統下載 .md 檔案，內容與編輯器一致
2. **Given** 使用者點擊「匯出 HTML」，**When** 系統轉換，**Then** 下載 .html 檔案，樣式美觀且程式碼高亮顯示
3. **Given** 使用者點擊「匯出 PDF」，**When** 系統轉換，**Then** 下載 .pdf 檔案，排版清晰適合列印
4. **Given** 使用者點擊「一鍵複製繳交版」，**When** 系統執行，**Then** 完整 Markdown 內容複製到剪貼簿，並顯示「已複製」提示

---

### User Story 5 - 從 GitHub Repo 提取專案資訊 (Priority: P3)

系統自動爬取提供的 GitHub Repo，讀取 README 和核心程式檔案，萃取專案結構、關鍵功能與技術細節，整合到筆記生成中。

**Why this priority**: GitHub 整合能讓筆記更完整，但不是核心必要功能（可以先靠對話紀錄和作業連結產出筆記）。

**Independent Test**: 提供一個 GitHub Repo URL，驗證系統能否正確讀取 README 和主要檔案，並在生成的筆記中反映這些資訊。

**Acceptance Scenarios**:

1. **Given** 使用者輸入 GitHub Repo URL，**When** 系統爬取，**Then** 成功讀取 README.md 和 src/ 目錄下主要檔案
2. **Given** 系統已讀取 Repo 內容，**When** 進行專案結構分析，**Then** 識別出專案類型（如 React App、Flask API）、主要模組與技術棧
3. **Given** 專案資訊已萃取，**When** 生成筆記時，**Then** 筆記包含「專案結構」段落，說明目錄組織與關鍵檔案
4. **Given** Repo 為私有或不存在，**When** 爬取失敗，**Then** 系統提示錯誤並繼續處理其他資料來源

---

### Edge Cases

- **空內容處理**: 若所有 Notion 連結的內容品質評分都低於門檻，系統應提示「未找到高品質內容，請檢查連結或手動提供素材」
- **爬蟲 rate limiting**: 當短時間內爬取多個 Notion 頁面時，系統必須遵守每秒最多 1 次請求的限制，避免被封鎖
- **大型檔案處理**: 若 GitHub Repo 超過 100MB 或檔案數超過 500 個，系統應僅分析 README 和主要目錄，避免處理超時
- **風格衝突**: 若老師 Blog 文章風格差異極大，系統應選擇最常見的模式作為主要風格
- **版本數量限制**: 編輯器自動儲存的版本數量超過 50 個時，系統應自動刪除最舊的版本（保留最近 50 個）
- **並發編輯**: MVP 階段不支援多人同時編輯同一份筆記（單使用者模式）
- **網路中斷**: 編輯過程中若網路中斷，系統應使用 localStorage 保存草稿，避免資料遺失
- **格式錯誤**: 若使用者貼入的 Markdown 包含無效語法（如未閉合的程式碼區塊），系統應自動修復或提示錯誤位置

## Requirements *(mandatory)*

### Functional Requirements

#### 爬蟲與資料擷取

- **FR-001**: 系統必須接受 Notion 公開頁面 URL 作為輸入，並爬取完整的 block-level 結構化內容（包含 block_id、block_type、text_content、hierarchy_level）
- **FR-002**: 系統必須接受 Blog/Substack URL 作為輸入，並擷取標題、發布日期、段落、程式碼區塊與列表
- **FR-003**: 系統必須接受 GitHub Repo URL，並讀取 README 與主要程式檔案（最多 50 個檔案）
- **FR-004**: 所有爬蟲行為必須遵守 robots.txt 並標註 User-Agent 為 "VibeCodingNoteBot/1.0"
- **FR-005**: 爬蟲失敗時，系統必須記錄錯誤原因（如 404、403、需登入）並提供手動貼上內容的 fallback 選項
- **FR-006**: 系統必須對每個爬取的資料來源記錄 URL、爬取時間戳與原始內容快照

#### 內容分析與評分

- **FR-007**: 系統必須對 Notion 內容進行 block-level 評分（0-100 分），評分維度包含結構清晰度、技術密度、可操作性、程式碼完整度
- **FR-008**: 系統必須僅保留評分高於 60 分的 blocks 作為「可學習內容」
- **FR-009**: 系統不得複製任何單一來源的原文句子，僅學習結構與風格模式
- **FR-010**: 系統必須產出每份作業的 document_aggregate_score（整體評分），並在 UI 中顯示

#### 風格學習與建模

- **FR-011**: 系統必須分析老師文章的段落順序、標題模式、教學句型與語氣特徵
- **FR-012**: 系統必須產生 style_profile.json，包含常見段落類型、標題命名模式與寫作節奏
- **FR-013**: 若無老師 Blog 資料，系統必須使用預設的「教學友善風格」模板

#### 筆記生成

- **FR-014**: 系統必須基於對話紀錄、GitHub Repo 與高品質 blocks 產出結構化 Markdown 筆記
- **FR-015**: 生成的筆記必須包含以下段落：專案摘要、核心功能說明、關鍵程式碼與解說、常見錯誤與解法
- **FR-016**: 生成的筆記必須套用 style_profile 中的風格特徵（標題格式、段落順序）
- **FR-017**: 每個程式碼區塊必須包含語言標註（如 ```python）與簡短解說

#### 線上編輯與版本控制

- **FR-018**: 系統必須提供 Markdown 線上編輯器，支援語法高亮與即時預覽
- **FR-019**: 編輯器必須每 30 秒自動儲存一次版本，或在使用者手動儲存時立即儲存
- **FR-020**: 系統必須支援 undo/redo 功能（至少 20 步操作歷史）
- **FR-021**: 系統必須在 UI 中顯示版本歷史列表（包含版本號、儲存時間、預覽前 50 字）
- **FR-022**: 使用者必須能夠還原到任一歷史版本，還原後該版本成為新的當前版本
- **FR-023**: 系統必須保留最近 50 個版本，超過時自動刪除最舊版本
- **FR-024**: 若瀏覽器崩潰或網路中斷，系統必須在 localStorage 保存編輯中的草稿

#### 匯出與交付

- **FR-025**: 系統必須支援匯出 Markdown 格式（.md 檔案）
- **FR-026**: 系統必須支援匯出 HTML 格式（.html 檔案，包含 CSS 樣式與程式碼高亮）
- **FR-027**: 系統必須支援匯出 PDF 格式（.pdf 檔案，排版適合列印）
- **FR-028**: 系統必須提供「一鍵複製繳交版」功能，將完整 Markdown 內容複製到剪貼簿

#### 資料隱私與合規

- **FR-029**: 系統不得爬取需要登入或付費訂閱的內容
- **FR-030**: 系統必須在爬取前檢查 robots.txt，若明確禁止則拒絕爬取
- **FR-031**: 所有使用者上傳的檔案與生成的筆記必須在 30 天後自動刪除
- **FR-032**: 系統不得儲存任何使用者的個人身份資訊（如 email、姓名）

#### API 與整合

- **FR-033**: 系統必須提供 POST /api/notion/import 端點，接受 Notion URL 並回傳結構化內容
- **FR-034**: 系統必須提供 POST /api/blog/import 端點，接受 Blog URL 並回傳擷取結果
- **FR-035**: 系統必須提供 POST /api/analyze 端點，執行內容評分並回傳 learnable_blocks
- **FR-036**: 系統必須提供 POST /api/style/build 端點，分析風格並回傳 style_profile.json
- **FR-037**: 系統必須提供 POST /api/generate 端點，接受所有輸入並產生筆記草稿
- **FR-038**: 系統必須提供 GET /api/doc/{id} 端點，回傳指定筆記的當前版本
- **FR-039**: 系統必須提供 PUT /api/doc/{id} 端點，更新筆記內容並自動建立新版本
- **FR-040**: 系統必須提供 POST /api/doc/{id}/restore 端點，還原到指定 version_id
- **FR-041**: 系統必須提供 POST /api/doc/{id}/export 端點，回傳指定格式的匯出檔案
- **FR-042**: 所有 API 錯誤必須回傳統一格式：`{"error": "錯誤描述", "code": "ERROR_CODE"}`
- **FR-043**: 所有 API 成功回應必須回傳統一格式：`{"success": true, "data": {...}}`
- **FR-044**: 系統必須提供 OpenAPI/Swagger 文件描述所有 API 端點

### Key Entities

- **Document**: 代表一份生成的筆記，包含 document_id、title、content（Markdown）、created_at、updated_at、current_version_id、data_sources（記錄所有爬取的 URL）
- **Version**: 代表筆記的歷史版本，包含 version_id、document_id、content、created_at、is_current（布林值，標示是否為最新版本）
- **DataSource**: 代表一個資料來源，包含 source_id、source_type（notion/blog/github）、url、fetched_at、raw_content_snapshot、quality_score（若為 Notion）
- **Block**: 代表 Notion 內容的單一區塊，包含 block_id、source_id、block_type（heading/paragraph/code/list）、text_content、hierarchy_level、quality_score（0-100）
- **StyleProfile**: 代表學習到的寫作風格，包含 profile_id、source_urls、common_heading_patterns、paragraph_order、teaching_tone、code_explanation_style、created_at
- **ExportJob**: 代表一次匯出任務，包含 job_id、document_id、format（markdown/html/pdf）、status（pending/completed/failed）、file_path、created_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者能在 10 分鐘內完成從輸入資料到產出筆記草稿的完整流程（包含爬取、分析、生成）
- **SC-002**: 系統能成功爬取至少 90% 的 Notion 公開頁面（排除因 rate limiting 或網路問題導致的失敗）
- **SC-003**: 生成的筆記草稿包含至少 3 個結構化段落（專案摘要、程式碼解說、常見問題）且無明顯邏輯錯誤
- **SC-004**: 編輯器的 undo/redo 功能在 100 次操作內正確運作，無資料遺失
- **SC-005**: 使用者能在 3 次點擊內完成筆記匯出（選擇格式 → 點擊匯出 → 下載檔案）
- **SC-006**: 風格學習功能能識別出老師文章中至少 5 個常見特徵（如標題模式、段落順序）
- **SC-007**: 系統在處理 3 個 Notion 連結 + 2 篇 Blog + 1 個 GitHub Repo 時，總處理時間不超過 5 分鐘
- **SC-008**: 生成的筆記中不得包含任何直接複製的原文句子（需通過文字比對驗證）
- **SC-009**: 版本自動儲存功能在 30 秒內觸發，且版本列表即時更新
- **SC-010**: 使用者在手動測試中對生成筆記的「可用性」滿意度達 70% 以上（可用性定義為：需要少量修改即可繳交）

## Assumptions *(optional)*

- 使用者提供的 Notion 連結均為公開頁面，無需驗證或權限
- GitHub Repo 為公開 Repo，不處理私有 Repo 的認證
- 對話紀錄 Markdown 檔案格式良好，包含清晰的問答結構
- 使用者使用現代瀏覽器（Chrome、Firefox、Safari 最新版本）且 JavaScript 已啟用
- 單次處理的資料來源數量不超過 10 個（Notion + Blog + GitHub 加總）
- 生成的筆記長度在 2000-10000 字之間（過短或過長可能影響品質）
- 老師 Blog 文章為中文或英文，系統暫不支援其他語言
- 爬取的 Notion 頁面內容總量不超過 50MB
- 系統運行於有穩定網路連線的環境
- MVP 階段為單使用者模式，無需考慮多人協作或權限管理

## Out of Scope *(optional)*

以下功能明確不在本次 MVP 範圍內：

- 多人即時協作編輯
- 使用者帳號系統與身份驗證
- 付費訂閱或權限管理
- 自動發布到 Medium、Notion 等平台
- AI 問答功能（例如「這段程式碼是做什麼的？」）
- 圖表與流程圖自動生成（未來可考慮）
- 支援影片或音訊內容的分析
- 移動端 App（僅支援 Web 版）
- 多語言支援（僅支援中文與英文混合內容）
- 即時通知（如「分析完成」推播）
- 與其他專案管理工具整合（如 Jira、Trello）

## Dependencies *(optional)*

- **外部服務**: Notion API（若使用官方 API）或 HTML 解析（若用爬蟲）
- **第三方套件**: Beautiful Soup 或 Playwright（爬蟲）、FastAPI 或 Flask（後端）、React 或 Vue（前端）、Monaco Editor 或 TipTap（編輯器）
- **資料庫**: SQLite（開發環境）或 PostgreSQL（生產環境）
- **AI 模型**: 若需要內容評分或風格學習，可能依賴 OpenAI API 或本地 LLM（如 Llama）

## Notes *(optional)*

- 本規格專注於 MVP 快速交付，不實作自動化測試，以手動 E2E 測試為主
- 所有 API 端點需提供完整的 Swagger 文件，方便前後端整合
- 爬蟲模組需特別注意 rate limiting 與 robots.txt 遵守，避免法律風險
- 風格學習模組的「不得複製原文」限制需透過文字相似度演算法驗證（如 cosine similarity < 0.7）
- 版本控制採用簡單的「快照」模式，每次儲存完整內容（非差異）以簡化實作
- 匯出 PDF 功能可使用 Puppeteer 或 wkhtmltopdf 進行 HTML → PDF 轉換
- 資料保留 30 天的政策需透過排程任務（cron job）定期清理過期資料
