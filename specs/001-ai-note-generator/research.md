# Technical Research & Decisions

**Feature**: Vibe Coding AI 學霸筆記生成器
**Phase**: 0 (Research)
**Date**: 2026-01-07

## 研究目的

本文件記錄 MVP 開發階段的技術選型研究與決策，遵循憲章「MVP 優先開發」與「程式碼簡潔」原則。

---

## 1. AI/NLP 模型選擇

### 最終決策：OpenAI API (GPT-3.5-turbo)

### 理由
- **快速啟動**：無需本地部署 LLM，直接 API 呼叫，符合 MVP 精神
- **品質保證**：GPT-3.5-turbo 足以完成內容評分與風格分析任務
- **成本可控**：估算每次筆記生成 < $0.1，MVP 階段可接受
- **簡化架構**：避免本地 LLM 需要的 GPU、記憶體、模型管理複雜度

### 替代方案評估

| 選項 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **OpenAI API (GPT-4)** | 品質最佳 | 成本高（每次 $0.5+） | ❌ 超出 MVP 預算 |
| **OpenAI API (GPT-3.5-turbo)** | 平衡成本與品質 | 需網路連線 | ✅ **最佳選擇** |
| **本地 LLM (Llama 2 13B)** | 無 API 費用，離線可用 | 需 GPU (24GB VRAM)，部署複雜 | ❌ 違反 MVP 簡潔原則 |
| **混合方案** | 彈性高 | 架構複雜，維護成本高 | ❌ 過度設計 |

### 實作建議
- 使用 `openai` Python SDK
- API Key 存放於環境變數 `.env`
- 實作 retry 機制（最多 3 次，指數退避）
- 記錄 API 用量與成本

---

## 2. Markdown 編輯器選擇

### 最終決策：Monaco Editor

### 理由
- **功能完整**：VS Code 核心編輯器，undo/redo、語法高亮、快捷鍵開箱即用
- **成熟穩定**：Microsoft 維護，文件完善，社群活躍
- **TypeScript 支援**：與前端技術棧一致
- **可自訂性**：支援自訂主題、語言定義、快捷鍵

### 替代方案評估

| 選項 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **Monaco Editor** | 功能強大，穩定 | Bundle 較大 (500KB gzip) | ✅ **最佳選擇** |
| **TipTap** | 輕量 (150KB)，WYSIWYG | Markdown 模式需額外設定 | ❌ MVP 優先功能完整性 |
| **CodeMirror 6** | 輕量 (200KB)，模組化 | 文件較少，學習曲線陡 | ❌ 開發時間成本高 |

### 實作建議
- 使用 `@monaco-editor/react` 套件
- 啟用 `markdown` 語言模式
- 設定 `minimap` 關閉以節省空間
- 實作自動儲存（監聽 `onChange` 事件，debounce 30 秒）

---

## 3. PDF 匯出實作方式

### 最終決策：Puppeteer (HTML → PDF)

### 理由
- **排版品質**：Chrome 渲染引擎，CSS 支援完整，適合圖文混排
- **中文支援**：無需額外設定字體
- **程式碼高亮**：HTML 可直接使用 highlight.js 渲染程式碼區塊
- **維護成本低**：與前端共用 HTML/CSS，不需獨立 PDF 模板

### 替代方案評估

| 選項 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **Puppeteer** | 排版品質高，中文完美支援 | 需在後端安裝 Chrome | ✅ **最佳選擇** |
| **wkhtmltopdf** | 命令列工具，輕量 | 已停止維護，CSS 支援有限 | ❌ 技術過時 |
| **jsPDF (前端)** | 純客戶端，無需後端 | 中文支援差，排版複雜 | ❌ 不符合需求 |

### 實作建議
- 後端安裝 `puppeteer` 與 Chromium
- 先將 Markdown 轉 HTML（使用 `marked` + `highlight.js`）
- 套用 CSS 樣式（適合列印的字體、行距、分頁）
- Puppeteer 設定：`format: 'A4', printBackground: true, margin: {top: '20mm', bottom: '20mm'}`

---

## 4. 爬蟲方案選擇

### 最終決策

| 資料來源 | 選擇方案 | 理由 |
|---------|---------|------|
| **Notion** | HTML 解析 (BeautifulSoup) | 公開頁面無需 API，簡單直接 |
| **Blog/Substack** | Playwright (JS 渲染) | 處理動態載入內容 |
| **GitHub** | GitHub API | 官方支援，穩定且有 rate limit 提示 |

### Notion 爬蟲

**決策**：使用 BeautifulSoup 解析 HTML

- **理由**：Notion 公開頁面不需認證，HTML 結構清晰
- **實作**：
  - 使用 `requests` GET 頁面 HTML
  - BeautifulSoup 解析 `<div class="notion-page-content">`
  - 識別 block type（heading, paragraph, code, callout, list）
  - 記錄 hierarchy_level（根據 heading level）

**風險**：Notion 改版可能導致解析失敗
**緩解**：提供手動貼上 fallback

### Blog/Substack 爬蟲

**決策**：使用 Playwright (JS 渲染)

- **理由**：許多部落格使用 JS 動態載入內容（如 Medium、Substack）
- **實作**：
  - Playwright 啟動 headless browser
  - 等待頁面載入完成 (`page.wait_for_load_state('networkidle')`)
  - 擷取 `<article>` 或 `<main>` 內容
  - 使用 BeautifulSoup 進一步解析結構

**替代**：若頁面為靜態 HTML，可 fallback 到 BeautifulSoup

### GitHub Repo 爬蟲

**決策**：使用 GitHub API

- **理由**：
  - 官方支援，穩定可靠
  - 提供 rate limit 資訊（5000 requests/hour 已認證，60 requests/hour 未認證）
  - 可直接讀取檔案內容（Base64 解碼）
- **實作**：
  - GET `/repos/{owner}/{repo}/contents/{path}` 遞迴讀取目錄
  - 限制：僅讀取 README + 最多 50 個主要檔案
  - 若 Repo 過大（> 100MB），僅讀取 README

**API Token**：暫不強制，MVP 階段接受 60 requests/hour 限制

### Rate Limiting 實作

**統一 Rate Limiter**：

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=1, per_seconds=1):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.requests = []

    def wait_if_needed(self):
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.per_seconds)
        self.requests = [req for req in self.requests if req > cutoff]

        if len(self.requests) >= self.max_requests:
            sleep_time = (self.requests[0] - cutoff).total_seconds()
            time.sleep(sleep_time + 0.1)

        self.requests.append(now)
```

- 每個爬蟲模組共用此 limiter
- 預設：每秒最多 1 次請求

---

## 5. 文字相似度演算法

### 最終決策：Cosine Similarity + TF-IDF

### 理由
- **準確度**：適合偵測語意相似的句子（即使字詞順序不同）
- **效能**：Python `scikit-learn` 提供高效實作
- **閾值明確**：相似度 > 0.7 視為「過度相似」，拒絕使用

### 實作建議

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_originality(generated_text, source_texts):
    """
    檢查生成文字是否直接複製來源
    :param generated_text: 生成的筆記內容
    :param source_texts: 所有來源文字（Notion blocks, Blog 段落）
    :return: (is_original, max_similarity)
    """
    vectorizer = TfidfVectorizer()
    all_texts = [generated_text] + source_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # 計算生成文字與每個來源的相似度
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    max_sim = similarities.max()

    return max_sim < 0.7, max_sim
```

### 替代方案評估

| 選項 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **Cosine Similarity + TF-IDF** | 語意準確，效能佳 | 需預處理文字 | ✅ **最佳選擇** |
| **Levenshtein Distance** | 簡單直觀 | 只能偵測字元級相似，無法處理改寫 | ❌ 不適合語意檢查 |
| **第三方 API (CopyScape)** | 專業工具 | 需費用，增加外部依賴 | ❌ MVP 不需要 |

---

## 6. 版本儲存策略

### 最終決策：完整快照模式

### 理由
- **實作簡單**：每次儲存直接寫入完整 Markdown 內容到資料庫
- **還原快速**：無需重建 diff，直接讀取版本內容
- **符合 MVP 原則**：避免差異演算法的複雜度

### 資料庫設計

```sql
CREATE TABLE versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,  -- 完整 Markdown 內容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE INDEX idx_version_document ON versions(document_id, created_at DESC);
```

### 空間估算
- 平均筆記大小：5KB (5000 字)
- 保留 50 個版本：250KB / 筆記
- 預估 100 份筆記：25MB
- **結論**：MVP 階段空間成本可接受

### 替代方案評估

| 選項 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **完整快照** | 簡單、快速 | 空間佔用較大 | ✅ **最佳選擇 (MVP)** |
| **差異儲存 (diff)** | 節省空間 (80% reduction) | 實作複雜，還原慢 | ❌ 過度設計 |

---

## 7. 前端狀態管理

### 最終決策：React Context + useReducer

### 理由
- **內建方案**：無需引入 Redux、Zustand 等第三方庫
- **足夠簡單**：編輯器狀態（undo/redo stack, current content）可用 reducer 管理
- **符合 MVP 原則**：避免過度抽象

### 實作建議

```typescript
// EditorContext.tsx
interface EditorState {
  content: string;
  history: string[];
  historyIndex: number;
  savedVersions: Version[];
}

type EditorAction =
  | { type: 'UPDATE_CONTENT'; content: string }
  | { type: 'UNDO' }
  | { type: 'REDO' }
  | { type: 'SAVE_VERSION'; version: Version };

const editorReducer = (state: EditorState, action: EditorAction): EditorState => {
  // 實作 undo/redo 邏輯
};
```

### 替代方案評估

| 選項 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **Context + useReducer** | 內建，零依賴 | 跨元件傳遞需 Context Provider | ✅ **最佳選擇** |
| **Redux** | 成熟，DevTools 強大 | 需學習 actions/reducers，boilerplate 多 | ❌ MVP 過重 |
| **Zustand** | 輕量，API 簡潔 | 引入外部依賴 | ❌ 憲章建議優先內建方案 |

---

## 8. 自動儲存實作

### 最終決策：前端 debounce + 後端 API

### 實作流程
1. 使用者編輯內容 → 觸發 `onChange` 事件
2. 前端 debounce 30 秒（使用 `lodash.debounce`）
3. 觸發時呼叫 `PUT /api/doc/{id}`（自動建立新版本）
4. 同時更新 localStorage（作為離線備份）

### 錯誤處理
- 若 API 失敗，localStorage 保留草稿
- 下次開啟編輯器時，檢查 localStorage 是否有未儲存草稿
- 若有，提示使用者：「偵測到未儲存的草稿，是否還原？」

---

## 總結

所有技術選型遵循以下原則：

✅ **MVP 優先**：選擇成熟、簡單的方案（OpenAI API、Monaco Editor、完整快照）
✅ **程式碼簡潔**：避免過度抽象（Context 而非 Redux，BeautifulSoup 而非自製解析器）
✅ **使用者體驗**：提供 fallback（手動貼上）、自動備份（localStorage）
✅ **資料隱私**：爬蟲遵守 robots.txt、標註 User-Agent
✅ **容錯設計**：API retry、爬蟲失敗獨立處理

下一階段將產出：
- `data-model.md` - 完整資料表設計
- `contracts/openapi.yaml` - API 規格
- `quickstart.md` - 開發環境設定指南
