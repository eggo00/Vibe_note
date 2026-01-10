# Data Model Design

**Feature**: Vibe Coding AI 學霸筆記生成器
**Phase**: 1.1 (Data Model)
**Date**: 2026-01-07
**Database**: SQLite (MVP), 可升級至 PostgreSQL

## 資料模型概覽

```
Document (1) ─┬─ Version (N)
              ├─ DataSource (N) ─── Block (N)
              └─ ExportJob (N)

StyleProfile (獨立表)
```

---

## 1. Document (筆記文件)

儲存每份生成的筆記主體資訊。

### Schema

```sql
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,           -- UUID v4
    title TEXT NOT NULL,                     -- 筆記標題
    content TEXT NOT NULL,                   -- 當前版本的 Markdown 內容
    current_version_id TEXT,                 -- 指向最新版本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_version_id) REFERENCES versions(version_id)
);

CREATE INDEX idx_document_updated ON documents(updated_at DESC);
```

### 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `document_id` | TEXT | UUID，唯一識別碼 | `"550e8400-e29b-41d4-a716-446655440000"` |
| `title` | TEXT | 筆記標題 | `"React Hooks 實作筆記"` |
| `content` | TEXT | 當前 Markdown 內容（冗餘儲存，加速讀取） | `"# 專案摘要\n..."` |
| `current_version_id` | TEXT | 最新版本 ID | `"v-123abc..."` |
| `created_at` | TIMESTAMP | 建立時間 | `"2026-01-07 10:30:00"` |
| `updated_at` | TIMESTAMP | 最後修改時間 | `"2026-01-07 15:45:00"` |

### 業務規則
- 每次編輯時同步更新 `content` 與 `updated_at`
- `current_version_id` 指向 versions 表的最新記錄
- 刪除文件時級聯刪除所有關聯的 versions, data_sources, export_jobs

---

## 2. Version (版本歷史)

儲存筆記的每個儲存點，採用完整快照模式。

### Schema

```sql
CREATE TABLE versions (
    version_id TEXT PRIMARY KEY,            -- UUID v4
    document_id TEXT NOT NULL,              -- 所屬文件
    content TEXT NOT NULL,                   -- 完整 Markdown 內容快照
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,        -- 是否為最新版本
    preview TEXT,                            -- 前 50 字預覽（用於 UI 顯示）
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX idx_version_document ON versions(document_id, created_at DESC);
CREATE INDEX idx_version_current ON versions(document_id, is_current);
```

### 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `version_id` | TEXT | UUID，版本唯一識別碼 | `"v-123abc..."` |
| `document_id` | TEXT | 所屬文件 ID | `"550e8400..."` |
| `content` | TEXT | 該版本的完整內容 | `"# 專案摘要\n..."` |
| `created_at` | TIMESTAMP | 版本建立時間 | `"2026-01-07 15:45:00"` |
| `is_current` | BOOLEAN | 是否為當前版本 | `TRUE` |
| `preview` | TEXT | 內容前 50 字 | `"# 專案摘要\n本專案實作一個 React..."` |

### 業務規則
- 每次自動儲存（30 秒）或手動儲存時建立新版本
- 同一 `document_id` 只有一個版本的 `is_current = TRUE`
- 保留最近 50 個版本，超過時刪除最舊版本（cron job 執行）
- 還原版本時：
  1. 新增一筆新的 version 記錄（copy 舊版本內容）
  2. 更新 document 的 `content` 與 `current_version_id`

---

## 3. DataSource (資料來源)

記錄用於生成筆記的所有資料來源（Notion, Blog, GitHub）。

### Schema

```sql
CREATE TABLE data_sources (
    source_id TEXT PRIMARY KEY,             -- UUID v4
    document_id TEXT NOT NULL,              -- 所屬文件
    source_type TEXT NOT NULL,               -- 'notion' | 'blog' | 'github'
    url TEXT NOT NULL,                       -- 來源 URL
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_content_snapshot TEXT,               -- 原始內容快照（JSON 格式）
    quality_score REAL,                      -- 整體品質評分（0-100，僅 Notion）
    metadata TEXT,                           -- 額外資訊（JSON：標題、作者等）
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX idx_source_document ON data_sources(document_id);
CREATE INDEX idx_source_type ON data_sources(source_type);
```

### 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `source_id` | TEXT | UUID | `"src-456def..."` |
| `document_id` | TEXT | 所屬文件 ID | `"550e8400..."` |
| `source_type` | TEXT | 來源類型 | `"notion"`, `"blog"`, `"github"` |
| `url` | TEXT | 來源 URL | `"https://notion.so/abc123"` |
| `fetched_at` | TIMESTAMP | 爬取時間 | `"2026-01-07 10:00:00"` |
| `raw_content_snapshot` | TEXT | 原始內容 JSON | `"{\"html\": \"<div>...</div>\"}"` |
| `quality_score` | REAL | Notion 整體評分 | `75.5` |
| `metadata` | TEXT | 額外資訊 JSON | `"{\"title\": \"React 教學\", \"author\": \"老師\"}"` |

### Metadata 範例

**Notion**:
```json
{
  "page_id": "abc123",
  "title": "React Hooks 作業",
  "total_blocks": 45,
  "learnable_blocks": 12
}
```

**Blog**:
```json
{
  "title": "深入理解 useState",
  "author": "老師",
  "publish_date": "2025-12-15",
  "word_count": 3500
}
```

**GitHub**:
```json
{
  "repo_name": "my-react-project",
  "branch": "main",
  "readme_path": "README.md",
  "file_count": 23
}
```

---

## 4. Block (Notion 內容區塊)

儲存 Notion 頁面的 block-level 內容與評分（僅用於 Notion 來源）。

### Schema

```sql
CREATE TABLE blocks (
    block_id TEXT PRIMARY KEY,              -- Notion block_id 或自生成 UUID
    source_id TEXT NOT NULL,                 -- 所屬資料來源
    block_type TEXT NOT NULL,                -- 'heading' | 'paragraph' | 'code' | 'list' | 'callout' | 'image'
    text_content TEXT,                       -- 文字內容
    code_language TEXT,                      -- 程式碼語言（block_type='code' 時）
    hierarchy_level INTEGER DEFAULT 0,       -- 標題層級（1=h1, 2=h2, ...）
    position_index INTEGER NOT NULL,         -- 區塊在頁面中的順序
    quality_score REAL NOT NULL,             -- Block 品質評分（0-100）
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE CASCADE
);

CREATE INDEX idx_block_source ON blocks(source_id, position_index);
CREATE INDEX idx_block_quality ON blocks(quality_score DESC);
```

### 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `block_id` | TEXT | Notion block_id 或 UUID | `"blk-789ghi..."` |
| `source_id` | TEXT | 所屬 data_source | `"src-456def..."` |
| `block_type` | TEXT | 區塊類型 | `"code"`, `"heading"`, `"paragraph"` |
| `text_content` | TEXT | 文字內容 | `"function App() { return <div>...</div>; }"` |
| `code_language` | TEXT | 程式語言 | `"javascript"`, `"python"` |
| `hierarchy_level` | INTEGER | 標題層級 | `2` (代表 h2) |
| `position_index` | INTEGER | 區塊順序 | `5` |
| `quality_score` | REAL | 品質評分 | `85.3` |

### 業務規則
- `quality_score >= 60` 的 blocks 視為「可學習內容」
- 品質評分維度（由 AI 評估）：
  - 結構清晰度（0-25 分）
  - 技術密度（0-25 分）
  - 可操作性（0-25 分）
  - 程式碼完整度（0-25 分）
- 僅儲存 Notion 來源的 blocks，Blog/GitHub 不使用此表

---

## 5. StyleProfile (寫作風格模型)

儲存從老師 Blog 分析出的寫作風格。

### Schema

```sql
CREATE TABLE style_profiles (
    profile_id TEXT PRIMARY KEY,            -- UUID v4
    name TEXT NOT NULL,                      -- 風格名稱（如「老師 Blog 風格」）
    source_urls TEXT NOT NULL,               -- 來源 URLs（JSON 陣列）
    common_heading_patterns TEXT,            -- 常見標題模式（JSON 陣列）
    paragraph_order TEXT,                    -- 段落順序模式（JSON 陣列）
    teaching_tone TEXT,                      -- 教學語氣（JSON：正式/友善/鼓勵等）
    code_explanation_style TEXT,             -- 程式碼解說風格（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                            -- 額外資訊（JSON）
);

CREATE INDEX idx_profile_name ON style_profiles(name);
```

### 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `profile_id` | TEXT | UUID | `"style-001"` |
| `name` | TEXT | 風格名稱 | `"老師 Substack 風格"` |
| `source_urls` | TEXT | 來源 URLs JSON | `["https://blog.com/post1", ...]` |
| `common_heading_patterns` | TEXT | 標題模式 JSON | `["## 核心概念", "## 實作步驟", ...]` |
| `paragraph_order` | TEXT | 段落順序 JSON | `["概念說明", "程式碼範例", "常見錯誤"]` |
| `teaching_tone` | TEXT | 語氣特徵 JSON | `{"formality": "friendly", "encouragement": true}` |
| `code_explanation_style` | TEXT | 程式碼解說 JSON | `{"pattern": "先整體後細節", "inline_comments": false}` |
| `created_at` | TIMESTAMP | 建立時間 | `"2026-01-07 11:00:00"` |
| `metadata` | TEXT | 額外資訊 | `{"article_count": 5, "avg_length": 3500}` |

### JSON 欄位範例

**common_heading_patterns**:
```json
[
  "## 專案摘要",
  "## 核心功能說明",
  "## 技術選型",
  "## 常見問題與解法"
]
```

**paragraph_order**:
```json
["intro", "concept", "code_example", "explanation", "common_errors", "tips"]
```

**teaching_tone**:
```json
{
  "formality": "friendly",
  "use_emoji": false,
  "encouragement_frequency": "moderate",
  "question_style": "rhetorical"
}
```

---

## 6. ExportJob (匯出任務)

記錄筆記匯出任務的狀態與結果。

### Schema

```sql
CREATE TABLE export_jobs (
    job_id TEXT PRIMARY KEY,                -- UUID v4
    document_id TEXT NOT NULL,              -- 所屬文件
    format TEXT NOT NULL,                    -- 'markdown' | 'html' | 'pdf'
    status TEXT DEFAULT 'pending',           -- 'pending' | 'processing' | 'completed' | 'failed'
    file_path TEXT,                          -- 匯出檔案路徑
    error_message TEXT,                      -- 錯誤訊息（若失敗）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX idx_export_document ON export_jobs(document_id);
CREATE INDEX idx_export_status ON export_jobs(status);
```

### 欄位說明

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `job_id` | TEXT | UUID | `"job-abc123"` |
| `document_id` | TEXT | 所屬文件 ID | `"550e8400..."` |
| `format` | TEXT | 匯出格式 | `"pdf"`, `"html"`, `"markdown"` |
| `status` | TEXT | 任務狀態 | `"completed"`, `"failed"` |
| `file_path` | TEXT | 檔案儲存路徑 | `"/tmp/exports/550e8400.pdf"` |
| `error_message` | TEXT | 錯誤訊息 | `"Puppeteer timeout after 30s"` |
| `created_at` | TIMESTAMP | 任務建立時間 | `"2026-01-07 16:00:00"` |
| `completed_at` | TIMESTAMP | 完成時間 | `"2026-01-07 16:02:00"` |

### 業務規則
- 匯出任務為非同步處理（若 PDF 生成時間較長）
- MVP 階段可同步處理（等待完成再回傳）
- 匯出檔案儲存於 `/tmp/exports/` 目錄，30 天後自動刪除

---

## 資料庫初始化 SQL

完整的資料庫建立腳本：

```sql
-- 1. Documents Table
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    current_version_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_updated ON documents(updated_at DESC);

-- 2. Versions Table
CREATE TABLE versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    preview TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX idx_version_document ON versions(document_id, created_at DESC);
CREATE INDEX idx_version_current ON versions(document_id, is_current);

-- 3. DataSources Table
CREATE TABLE data_sources (
    source_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    url TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_content_snapshot TEXT,
    quality_score REAL,
    metadata TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX idx_source_document ON data_sources(document_id);
CREATE INDEX idx_source_type ON data_sources(source_type);

-- 4. Blocks Table
CREATE TABLE blocks (
    block_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    block_type TEXT NOT NULL,
    text_content TEXT,
    code_language TEXT,
    hierarchy_level INTEGER DEFAULT 0,
    position_index INTEGER NOT NULL,
    quality_score REAL NOT NULL,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE CASCADE
);

CREATE INDEX idx_block_source ON blocks(source_id, position_index);
CREATE INDEX idx_block_quality ON blocks(quality_score DESC);

-- 5. StyleProfiles Table
CREATE TABLE style_profiles (
    profile_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_urls TEXT NOT NULL,
    common_heading_patterns TEXT,
    paragraph_order TEXT,
    teaching_tone TEXT,
    code_explanation_style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

CREATE INDEX idx_profile_name ON style_profiles(name);

-- 6. ExportJobs Table
CREATE TABLE export_jobs (
    job_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    format TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    file_path TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX idx_export_document ON export_jobs(document_id);
CREATE INDEX idx_export_status ON export_jobs(status);
```

---

## 資料保留政策

遵循憲章「資料隱私與合規」原則，實作 30 天自動刪除：

### Cron Job 腳本 (`scripts/cleanup_old_data.py`)

```python
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

def cleanup_old_data():
    """刪除 30 天前的資料"""
    engine = create_engine('sqlite:///vibe_note.db')
    cutoff_date = datetime.now() - timedelta(days=30)

    with engine.connect() as conn:
        # 刪除舊文件（級聯刪除關聯資料）
        result = conn.execute(
            text("DELETE FROM documents WHERE created_at < :cutoff"),
            {"cutoff": cutoff_date}
        )
        print(f"Deleted {result.rowcount} documents older than {cutoff_date}")

        # 刪除舊的匯出檔案
        conn.execute(
            text("DELETE FROM export_jobs WHERE completed_at < :cutoff"),
            {"cutoff": cutoff_date}
        )

        conn.commit()

if __name__ == "__main__":
    cleanup_old_data()
```

### Crontab 設定

```bash
# 每天凌晨 2:00 執行清理
0 2 * * * /usr/bin/python3 /path/to/scripts/cleanup_old_data.py
```

---

## ORM 對應（SQLAlchemy）

### 後端模型範例

```python
# backend/src/models/document.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    current_version_id = Column(String, ForeignKey("versions.version_id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Version(Base):
    __tablename__ = "versions"

    version_id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_current = Column(Boolean, default=False)
    preview = Column(Text)
```

---

## 總結

資料模型設計完成，涵蓋：

✅ **6 張核心資料表**：Document, Version, DataSource, Block, StyleProfile, ExportJob
✅ **完整欄位定義**：包含型別、預設值、外鍵關聯
✅ **索引優化**：針對常用查詢建立索引
✅ **資料保留政策**：30 天自動刪除機制
✅ **ORM 對應**：SQLAlchemy 模型範例

下一步：建立 API 合約 (`contracts/openapi.yaml`)
