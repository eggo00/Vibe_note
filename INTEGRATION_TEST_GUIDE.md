# 整合測試指南

Phase 3 前後端整合測試執行步驟

---

## 📋 測試準備

### 1. 環境需求檢查

```bash
# 檢查 Python 版本
python --version  # 應為 3.11+

# 檢查 Node.js 版本
node --version   # 應為 18+

# 檢查 UV 是否安裝
uv --version
```

### 2. 設定環境變數

**後端 `.env` 檔案**:
```bash
cd backend
cat > .env << 'EOF'
# OpenAI API Key (必填！)
OPENAI_API_KEY=sk-your-actual-api-key-here

# 資料庫
DATABASE_URL=sqlite:///./vibe_note.db

# 伺服器設定
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS（允許前端跨域）
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 爬蟲與評分設定
RATE_LIMIT_PER_SECOND=1
QUALITY_SCORE_THRESHOLD=60.0
SIMILARITY_THRESHOLD=0.7
EOF
```

**前端 `.env` 檔案**:
```bash
cd ../frontend
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
```

### 3. 初始化資料庫

```bash
cd ../backend
uv run python scripts/init_db.py
```

---

## 🚀 啟動服務

### 終端機 1: 啟動後端 API

```bash
cd backend

# 安裝依賴（首次執行）
uv venv
uv pip install -r requirements.txt

# 啟動 FastAPI
uv run python -m src.main
```

**預期輸出**:
```
==================================================
🚀 Vibe Note API 啟動中...
📊 資料庫: sqlite:///./vibe_note.db
🌐 CORS 允許來源: http://localhost:5173, http://localhost:3000
🔧 環境: Development
📖 API 文件: http://0.0.0.0:8000/docs
==================================================
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **驗證後端**: 開啟瀏覽器訪問 http://localhost:8000/docs

### 終端機 2: 啟動前端應用

```bash
cd frontend

# 安裝依賴（首次執行）
npm install

# 啟動開發伺服器
npm run dev
```

**預期輸出**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ **驗證前端**: 開啟瀏覽器訪問 http://localhost:5173/

---

## 🧪 整合測試流程

### 測試 1: API 健康檢查

**使用 curl**:
```bash
# 測試健康檢查端點
curl http://localhost:8000/health

# 預期回應
{
  "status": "healthy",
  "timestamp": "2026-01-10T...",
  "version": "1.0.0",
  "database": "connected"
}
```

**使用 Swagger UI**:
1. 訪問 http://localhost:8000/docs
2. 展開 `GET /health`
3. 點擊 "Try it out" → "Execute"
4. 檢查回應狀態碼為 200

---

### 測試 2: Notion 匯入功能

**步驟 2.1: 準備測試 URL**
找一個公開的 Notion 頁面，例如：
```
https://www.notion.so/Example-Page-xxxxx
```

⚠️ **注意**:
- 確保頁面已設為「公開分享」
- 避免使用有 robots.txt 限制的頁面

**步驟 2.2: 使用 Swagger UI 測試**
1. 訪問 http://localhost:8000/docs
2. 找到 `POST /api/notion/import`
3. 點擊 "Try it out"
4. 輸入請求內容:
```json
{
  "url": "https://www.notion.so/your-test-page-url"
}
```
5. 點擊 "Execute"
6. **預期回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "source_id": "uuid-here",
    "url": "https://www.notion.so/...",
    "blocks_count": 15,
    "robots_allowed": true,
    "fetched_at": "2026-01-10T..."
  }
}
```

**記下 `source_id`** 以供後續測試使用！

---

### 測試 3: 內容品質分析

**步驟 3.1: 使用 Swagger UI**
1. 找到 `POST /api/analyze`
2. 輸入剛才取得的 `source_id`:
```json
{
  "source_id": "剛才的-uuid"
}
```
3. 點擊 "Execute"
4. **預期回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "source_id": "...",
    "total_blocks": 15,
    "high_quality_blocks": 8,
    "average_score": 72.5,
    "threshold": 60.0,
    "blocks": [...]
  }
}
```

**驗證點**:
- ✅ `high_quality_blocks` > 0
- ✅ `average_score` 介於 0-100
- ✅ `blocks` 陣列包含評分詳情

---

### 測試 4: 筆記生成

**步驟 4.1: 使用 Swagger UI**
1. 找到 `POST /api/generate`
2. 輸入請求:
```json
{
  "source_id": "剛才的-uuid",
  "title": "React Hooks 學習筆記",
  "project_context": "這是一個 React 學習專案"
}
```
3. 點擊 "Execute"
4. **預期回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "document_id": "doc-uuid",
    "version_id": "ver-uuid",
    "title": "React Hooks 學習筆記",
    "content_preview": "# React Hooks 學習筆記\n\n## 專案摘要...",
    "total_blocks_used": 8,
    "quality_score": 72.5
  }
}
```

**記下 `document_id`** 以供前端測試使用！

---

### 測試 5: 文件查詢

**步驟 5.1: 使用 Swagger UI**
1. 找到 `GET /api/doc/{document_id}`
2. 輸入剛才的 `document_id`
3. 點擊 "Execute"
4. **預期回應**:
```json
{
  "success": true,
  "data": {
    "document_id": "...",
    "title": "React Hooks 學習筆記",
    "content": "完整的 Markdown 內容...",
    "current_version_id": "...",
    "aggregate_score": 72.5,
    "version_count": 1
  }
}
```

**驗證點**:
- ✅ `content` 包含完整 Markdown
- ✅ `version_count` 為 1
- ✅ 包含四個段落（專案摘要、核心功能、程式碼範例、常見錯誤）

---

### 測試 6: 前端整合流程

**步驟 6.1: 訪問首頁**
1. 開啟 http://localhost:5173/
2. 應看到漂亮的漸層背景頁面
3. 標題：「🎓 Vibe Note AI 學霸筆記生成器」

**步驟 6.2: 輸入 Notion URL**
1. 在輸入框貼上測試 URL
2. 點擊「開始分析」
3. **預期行為**:
   - ✅ 顯示「正在爬取 Notion 頁面...」
   - ✅ 進度條開始移動（0% → 25%）
   - ✅ 切換到「正在分析內容品質...」（50%）
   - ✅ 切換到「正在生成筆記...」（75%）
   - ✅ 顯示「完成！」（100%）
   - ✅ 顯示分析結果統計

**步驟 6.3: 自動導向文件頁面**
1. 完成後應自動跳轉到 `/document/{id}`
2. **預期顯示**:
   - ✅ 文件標題
   - ✅ 版本資訊、品質分數
   - ✅ 完整的 Markdown 內容
   - ✅ 返回按鈕

---

## 🐛 錯誤情境測試

### 測試 7: 無效 URL 處理

**前端測試**:
1. 輸入無效 URL: `https://google.com`
2. **預期行為**:
   - ✅ 顯示錯誤訊息
   - ✅ 提供「手動貼上內容」選項
   - ✅ 提供「重新開始」按鈕

**API 測試**:
```bash
curl -X POST http://localhost:8000/api/notion/import \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# 預期：錯誤回應
```

---

### 測試 8: robots.txt 限制

**測試步驟**:
1. 使用被 robots.txt 禁止的 URL
2. **預期回應**:
```json
{
  "error": "robots.txt 禁止爬取此頁面",
  "code": "SCRAPE_FORBIDDEN"
}
```

---

### 測試 9: OpenAI API Key 未設定

**測試步驟**:
1. 暫時移除 `.env` 中的 `OPENAI_API_KEY`
2. 重啟後端
3. 嘗試分析內容
4. **預期錯誤**:
```json
{
  "error": "AI 評分器初始化失敗：OPENAI_API_KEY 未設定",
  "code": "AI_API_ERROR"
}
```

---

## ✅ 測試檢查清單

### 後端 API
- [ ] ✅ GET /health 回應正常
- [ ] ✅ POST /api/notion/import 成功匯入
- [ ] ✅ POST /api/analyze 成功評分
- [ ] ✅ POST /api/generate 成功生成筆記
- [ ] ✅ GET /api/doc/{id} 取得文件內容
- [ ] ✅ 錯誤情境正確處理

### 前端應用
- [ ] ✅ 首頁正確載入
- [ ] ✅ URL 輸入驗證正常
- [ ] ✅ 進度顯示流暢
- [ ] ✅ 自動導向文件頁面
- [ ] ✅ 文件內容正確顯示
- [ ] ✅ 錯誤訊息友善

### 整合流程
- [ ] ✅ 完整流程：輸入 → 爬取 → 分析 → 生成 → 顯示
- [ ] ✅ 所有 API 回應格式一致
- [ ] ✅ CORS 設定正確（無跨域錯誤）
- [ ] ✅ 資料庫正確儲存

---

## 🔍 偵錯技巧

### 查看後端日誌
```bash
# 後端終端機會顯示所有 API 請求
# 範例：
INFO:     127.0.0.1:xxxxx - "POST /api/notion/import HTTP/1.1" 200 OK
```

### 查看前端 Console
1. 開啟瀏覽器開發者工具（F12）
2. 切換到 Console 標籤
3. 查看 API 呼叫與錯誤訊息

### 查看網路請求
1. 開發者工具 → Network 標籤
2. 過濾 `Fetch/XHR`
3. 檢查請求與回應內容

### 資料庫檢查
```bash
cd backend
sqlite3 vibe_note.db

# 檢查資料
SELECT * FROM data_sources;
SELECT * FROM blocks LIMIT 5;
SELECT * FROM documents;
SELECT * FROM versions;
```

---

## 🎯 成功標準

整合測試通過的條件：

1. ✅ 後端 API 所有端點回應正常
2. ✅ 前端能成功呼叫後端 API
3. ✅ 完整流程能順利執行到底
4. ✅ 生成的筆記包含四個必要段落
5. ✅ 錯誤情境有友善提示
6. ✅ 資料正確儲存到資料庫

---

## 📝 測試報告範本

完成測試後，填寫以下報告：

```markdown
# 整合測試報告

**測試日期**: 2026-01-10
**測試人員**: [您的名字]

## 測試環境
- Python: [版本]
- Node.js: [版本]
- OpenAI API: [有效/無效]

## 測試結果

### 後端 API
- [ ] 健康檢查: PASS / FAIL
- [ ] Notion 匯入: PASS / FAIL
- [ ] 內容分析: PASS / FAIL
- [ ] 筆記生成: PASS / FAIL
- [ ] 文件查詢: PASS / FAIL

### 前端應用
- [ ] 首頁載入: PASS / FAIL
- [ ] 完整流程: PASS / FAIL
- [ ] 錯誤處理: PASS / FAIL

### 發現的問題
1. [問題描述]
2. [問題描述]

### 建議改進
1. [改進建議]
2. [改進建議]
```

---

## 🚀 下一步

測試通過後：
1. 記錄測試結果
2. 修正發現的問題
3. 準備部署到測試環境
4. 進行用戶驗收測試（UAT）

測試失敗時：
1. 檢查錯誤日誌
2. 參考偵錯技巧排查
3. 修正問題後重新測試
