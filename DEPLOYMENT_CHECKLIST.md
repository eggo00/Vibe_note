# Zeabur 部署檢查清單

快速檢查清單，確保部署順利。

## 📋 部署前準備

### 1. 代碼準備
- [x] 後端 Dockerfile 已建立 (`backend/Dockerfile`)
- [x] 前端 Dockerfile 已建立 (`frontend/Dockerfile`)
- [x] .dockerignore 已建立（後端、前端）
- [x] Nginx 配置已建立 (`frontend/nginx.conf`)
- [x] 資料庫自動初始化已啟用（`src/main.py`）

### 2. 推送到 GitHub
```bash
git add .
git commit -m "feat: 準備部署到 Zeabur"
git push origin main
```

---

## 🚀 Zeabur 部署步驟

### 步驟 1: 建立專案
- [ ] 登入 Zeabur Dashboard
- [ ] 點擊 "Create Project"
- [ ] 專案名稱: `vibe-note`

### 步驟 2: 部署後端
- [ ] Add Service → Git → 選擇倉庫
- [ ] 服務名稱: `vibe-note-backend`
- [ ] Root Directory: `backend`
- [ ] 等待自動偵測 Dockerfile

**環境變數設定**:
```bash
DATABASE_URL=sqlite:///./data/vibe_note.db
CORS_ORIGINS=https://your-frontend.zeabur.app
QUALITY_SCORE_THRESHOLD=60.0
USE_MOCK_AI=True
# OPENAI_API_KEY=sk-xxx  # 如果使用真實 API
```

**Volume 持久化**:
- [ ] Mount Path: `/app/data`
- [ ] Size: 1 GB

**取得後端 URL**:
- [ ] 複製後端網域: `_________________.zeabur.app`

### 步驟 3: 部署前端
- [ ] Add Service → Git → 選擇相同倉庫
- [ ] 服務名稱: `vibe-note-frontend`
- [ ] Root Directory: `frontend`

**環境變數設定**:
```bash
VITE_API_URL=https://your-backend-url.zeabur.app
```
（將上面複製的後端 URL 填入）

**取得前端 URL**:
- [ ] 複製前端網域: `_________________.zeabur.app`

### 步驟 4: 更新 CORS 設定
- [ ] 回到後端服務
- [ ] 更新環境變數 `CORS_ORIGINS`
- [ ] 填入前端 URL
- [ ] 點擊 "Redeploy"

---

## ✅ 部署驗證

### 測試後端
訪問: `https://your-backend.zeabur.app/health`

預期回應:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "database": "healthy"
  }
}
```

### 測試前端
- [ ] 訪問: `https://your-frontend.zeabur.app`
- [ ] 看到 Vibe Note 首頁
- [ ] 輸入 Notion URL 測試
- [ ] 成功生成筆記

### 測試 API 文件
訪問: `https://your-backend.zeabur.app/docs`
- [ ] Swagger UI 正常顯示

---

## 🔧 環境變數總覽

### 後端環境變數
| 變數名稱 | 必填 | 範例值 | 說明 |
|---------|------|--------|------|
| `DATABASE_URL` | ✅ | `sqlite:///./data/vibe_note.db` | 資料庫路徑 |
| `CORS_ORIGINS` | ✅ | `https://your-frontend.zeabur.app` | CORS 允許來源 |
| `QUALITY_SCORE_THRESHOLD` | ✅ | `60.0` | 品質門檻 |
| `USE_MOCK_AI` | ✅ | `True` | 是否使用 Mock AI |
| `OPENAI_API_KEY` | ❌ | `sk-xxx` | OpenAI API Key（Mock 模式不需要） |

### 前端環境變數
| 變數名稱 | 必填 | 範例值 | 說明 |
|---------|------|--------|------|
| `VITE_API_URL` | ✅ | `https://your-backend.zeabur.app` | 後端 API URL |

---

## 🐛 常見問題快速排查

### 前端無法連接後端
1. 檢查 `VITE_API_URL` 是否正確
2. 檢查 `CORS_ORIGINS` 是否包含前端網域
3. 重新部署兩個服務

### 資料庫資料丟失
1. 確認後端 Volume 已啟用
2. 確認 Mount Path 為 `/app/data`
3. 確認 DATABASE_URL 為 `sqlite:///./data/vibe_note.db`

### 部署失敗
1. 查看 Zeabur 部署日誌
2. 檢查 Dockerfile 語法
3. 檢查 Root Directory 設定

### 服務無法啟動
1. 查看服務日誌
2. 確認環境變數已設定
3. 確認端口設定正確

---

## 📝 記錄您的部署資訊

**後端 URL**: `_____________________________________________`

**前端 URL**: `_____________________________________________`

**部署日期**: `_____________________________________________`

**使用方案**: □ Free  □ Pro

**備註**:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🎉 部署完成！

恭喜！您的 Vibe Note 已成功部署到 Zeabur。

下一步:
1. 分享給朋友測試
2. 收集使用反饋
3. 持續優化功能

詳細部署指南: 查看 `ZEABUR_DEPLOYMENT_GUIDE.md`
