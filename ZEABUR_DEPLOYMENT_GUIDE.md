# Vibe Note - Zeabur 部署指南

本指南將協助您將 Vibe Note 部署到 Zeabur 平台。

## 前置準備

1. **Zeabur 帳號**: 註冊 [Zeabur](https://zeabur.com/)
2. **GitHub 倉庫**: 將專案推送到 GitHub
3. **環境變數**: 準備必要的環境變數

---

## 部署步驟

### 步驟 1: 推送代碼到 GitHub

```bash
# 如果尚未初始化 Git 倉庫
git init
git add .
git commit -m "feat: 準備部署到 Zeabur"

# 連接到您的 GitHub 倉庫
git remote add origin https://github.com/YOUR_USERNAME/Vibe_note.git
git branch -M main
git push -u origin main
```

### 步驟 2: 在 Zeabur 建立專案

1. 登入 [Zeabur Dashboard](https://dash.zeabur.com/)
2. 點擊 **"Create Project"** 建立新專案
3. 為專案命名（如：`vibe-note`）

### 步驟 3: 部署後端服務

#### 3.1 建立後端服務

1. 在專案中點擊 **"Add Service"**
2. 選擇 **"Git"**
3. 選擇您的 GitHub 倉庫 `Vibe_note`
4. Zeabur 會自動偵測到 `backend/Dockerfile`

#### 3.2 設定後端服務

**服務名稱**: `vibe-note-backend`

**根目錄**: 設定為 `backend`
- 在服務設定中找到 "Root Directory"
- 輸入: `backend`

**環境變數設定**:

點擊服務設定 → Environment Variables，新增以下變數：

```bash
# 資料庫設定
DATABASE_URL=sqlite:///./data/vibe_note.db

# CORS 設定（前端 URL，部署後需更新）
CORS_ORIGINS=https://your-frontend.zeabur.app

# 品質門檻
QUALITY_SCORE_THRESHOLD=60.0

# Mock AI 模式（生產環境建議關閉，使用真實 OpenAI API）
USE_MOCK_AI=True

# OpenAI API Key（如果不使用 Mock 模式）
# OPENAI_API_KEY=sk-your-openai-api-key
```

**端口設定**:
- Zeabur 會自動偵測端口 8000

#### 3.3 啟用持久化儲存（重要！）

為了保存資料庫：

1. 在後端服務設定中找到 **"Volumes"**
2. 新增 Volume:
   - **Mount Path**: `/app/data`
   - **Size**: 1 GB（或根據需求調整）

### 步驟 4: 部署前端服務

#### 4.1 建立前端服務

1. 在同一專案中再次點擊 **"Add Service"**
2. 選擇 **"Git"**
3. 選擇相同的 GitHub 倉庫
4. Zeabur 會偵測到 `frontend/Dockerfile`

#### 4.2 設定前端服務

**服務名稱**: `vibe-note-frontend`

**根目錄**: 設定為 `frontend`
- 在服務設定中找到 "Root Directory"
- 輸入: `frontend`

**環境變數設定**:

```bash
# API 後端 URL（使用後端服務的 URL）
VITE_API_URL=https://your-backend.zeabur.app
```

**重要**: 部署後端後，複製後端的 URL 並填入 `VITE_API_URL`

**端口設定**:
- 前端使用端口 80（Nginx）

### 步驟 5: 設定網域（選填）

#### 為後端服務設定網域

1. 點擊後端服務
2. 進入 "Networking" 或 "Domain"
3. 選擇：
   - **Zeabur 提供的免費子網域**: `your-backend.zeabur.app`
   - **自訂網域**: 綁定您自己的網域

#### 為前端服務設定網域

1. 點擊前端服務
2. 進入 "Networking" 或 "Domain"
3. 設定：
   - **Zeabur 提供的免費子網域**: `your-frontend.zeabur.app`
   - **自訂網域**: 綁定您自己的網域

### 步驟 6: 更新環境變數

部署完成後，更新環境變數以使用正確的 URL：

#### 更新後端 CORS 設定

```bash
CORS_ORIGINS=https://your-frontend.zeabur.app,https://your-custom-domain.com
```

#### 更新前端 API URL

```bash
VITE_API_URL=https://your-backend.zeabur.app
```

**重要**: 每次更新環境變數後，需要重新部署服務：
- 點擊服務 → "Redeploy"

---

## 初始化資料庫

部署完成後，需要初始化資料庫：

### 方法 1: 使用 Zeabur Web Terminal

1. 在後端服務頁面，找到 **"Terminal"** 或 **"Console"**
2. 執行初始化腳本：

```bash
python scripts/init_db.py
```

### 方法 2: 自動初始化

修改 `backend/src/main.py`，在應用啟動時自動建立資料表（建議）：

```python
# 已經在 src/main.py 中實現
# 啟動時會自動建立資料表
```

---

## 驗證部署

### 測試後端 API

訪問：`https://your-backend.zeabur.app/health`

應該返回：
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "database": "healthy"
  }
}
```

訪問：`https://your-backend.zeabur.app/docs`
- 可以查看完整的 API 文件（Swagger UI）

### 測試前端應用

訪問：`https://your-frontend.zeabur.app`
- 應該看到 Vibe Note 首頁
- 測試輸入 Notion URL 並生成筆記

---

## 生產環境建議

### 1. 使用真實的 OpenAI API

```bash
# 在後端環境變數中設定
USE_MOCK_AI=False
OPENAI_API_KEY=sk-your-real-openai-api-key
```

### 2. 啟用 HTTPS

Zeabur 預設提供 HTTPS，確保所有 URL 使用 `https://`

### 3. 設定資料庫備份

定期備份 SQLite 資料庫：
- 使用 Zeabur Volume 的備份功能
- 或考慮升級到 PostgreSQL（Zeabur 支援）

### 4. 監控與日誌

- 在 Zeabur Dashboard 查看服務日誌
- 監控服務狀態和效能

### 5. 環境變數安全

- 不要在代碼中寫死敏感資訊
- 使用 Zeabur 的環境變數管理

---

## 常見問題

### Q1: 前端無法連接到後端

**解決方法**:
1. 檢查前端環境變數 `VITE_API_URL` 是否正確
2. 檢查後端 `CORS_ORIGINS` 是否包含前端網域
3. 重新部署兩個服務

### Q2: 資料庫資料丟失

**解決方法**:
1. 確認後端服務已啟用 Volume 持久化
2. Mount Path 設定為 `/app/data`
3. 資料庫路徑使用 `/app/data/vibe_note.db`

### Q3: 部署失敗

**檢查事項**:
1. 查看 Zeabur 部署日誌
2. 確認 Dockerfile 語法正確
3. 確認 `requirements.txt` 或 `package.json` 正確
4. 檢查 Root Directory 設定

### Q4: 服務啟動但無法訪問

**解決方法**:
1. 檢查服務是否正在運行（查看日誌）
2. 確認端口設定正確
3. 檢查網域綁定是否生效

---

## 成本估算

Zeabur 定價（參考）:
- **免費方案**: 適合開發測試
  - 限制: 有限的運算資源和流量
- **Pro 方案**: 適合生產環境
  - 約 $5-10 USD/月（視資源使用量）

---

## 部署後檢查清單

- [ ] 後端服務成功部署並可訪問 `/health`
- [ ] 前端服務成功部署並可訪問首頁
- [ ] 資料庫已初始化（可以建立筆記）
- [ ] CORS 設定正確（前端可以呼叫後端 API）
- [ ] 環境變數已正確設定
- [ ] Volume 持久化已啟用（資料不會丟失）
- [ ] 網域已設定（如果需要）
- [ ] 測試完整流程：輸入 Notion URL → 生成筆記

---

## 下一步

部署成功後，您可以：

1. **監控服務**: 定期檢查 Zeabur Dashboard
2. **收集反饋**: 邀請用戶測試
3. **持續改進**: 根據用戶反饋優化功能
4. **擴展功能**: 實現更多進階功能

---

## 需要幫助？

- Zeabur 文件: https://zeabur.com/docs
- Zeabur Discord: https://discord.gg/zeabur
- GitHub Issues: 在您的倉庫提交問題

祝您部署順利！🚀
