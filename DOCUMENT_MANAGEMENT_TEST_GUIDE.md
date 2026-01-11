# 文件管理功能測試指南

## 您的測試文件資訊

- **Document ID**: `36c37289-3816-40cc-98cd-d697c71394d4`
- **標題**: Chrome Plugin｜Meet Chat Logger - 學習筆記
- **當前版本 ID**: `29fcc98a-d346-41c7-8dc8-89897e964242`
- **品質分數**: 63.3
- **版本數**: 1

## 開始測試

### 1. 打開 Swagger UI

在瀏覽器訪問：**http://localhost:8000/docs**

您會看到 FastAPI 自動生成的 API 文件介面。

---

## 測試功能清單

### 測試 1: 取得文件詳情

**API**: `GET /api/doc/{document_id}`

1. 在 Swagger UI 中找到 **Documents** 標籤並展開
2. 點擊 `GET /api/doc/{document_id}`
3. 點擊右上角的 **"Try it out"** 按鈕
4. 在 `document_id` 欄位輸入：
   ```
   36c37289-3816-40cc-98cd-d697c71394d4
   ```
5. 點擊 **"Execute"** 按鈕
6. 查看回應結果，應該包含：
   - 文件標題
   - 完整 Markdown 內容
   - 版本數量
   - 品質分數
   - 建立/更新時間

**預期結果**: 返回完整的文件資訊和內容

---

### 測試 2: 查看版本歷史

**API**: `GET /api/doc/{document_id}/versions`

1. 找到 `GET /api/doc/{document_id}/versions`
2. 點擊 **"Try it out"**
3. 輸入 document_id：
   ```
   36c37289-3816-40cc-98cd-d697c71394d4
   ```
4. 點擊 **"Execute"**
5. 查看回應，應該顯示：
   - 總版本數: 1
   - 版本列表（包含版本號、建立時間、內容預覽）

**預期結果**: 返回版本歷史列表

---

### 測試 3: 更新文件內容（建立新版本）

**API**: `PUT /api/doc/{document_id}`

1. 找到 `PUT /api/doc/{document_id}`
2. 點擊 **"Try it out"**
3. 輸入 document_id：
   ```
   36c37289-3816-40cc-98cd-d697c71394d4
   ```
4. 在 Request body 區域輸入：
   ```json
   {
     "content": "# 技術學習筆記 - 更新版\n\n## 專案摘要\n\n這是更新後的內容，用於測試版本管理功能。\n\n## 新增內容\n\n1. 測試版本控制\n2. 測試內容更新\n3. 測試自動建立新版本\n\n---\n\n**版本 2** - 手動更新測試",
     "change_summary": "測試版本管理：新增更新內容"
   }
   ```
5. 點擊 **"Execute"**
6. 查看回應，應該包含：
   - 新的 version_id
   - version_number: 2
   - 變更摘要

**預期結果**: 成功建立版本 2

---

### 測試 4: 再次查看版本歷史

重複**測試 2**，這次應該會看到：
- 總版本數: 2
- 兩個版本的列表（版本 2 和版本 1）

---

### 測試 5: 查看特定版本內容

**API**: `GET /api/doc/{document_id}/version/{version_id}`

**查看版本 1（原始版本）：**

1. 找到 `GET /api/doc/{document_id}/version/{version_id}`
2. 點擊 **"Try it out"**
3. 輸入參數：
   - document_id: `36c37289-3816-40cc-98cd-d697c71394d4`
   - version_id: `29fcc98a-d346-41c7-8dc8-89897e964242`
4. 點擊 **"Execute"**
5. 查看回應，應該顯示：
   - version_number: 1
   - is_current: false（因為已更新到版本 2）
   - 原始的完整內容

**預期結果**: 返回版本 1 的完整內容

---

### 測試 6: 恢復到舊版本

**API**: `POST /api/doc/{document_id}/restore/{version_id}`

**恢復到版本 1：**

1. 找到 `POST /api/doc/{document_id}/restore/{version_id}`
2. 點擊 **"Try it out"**
3. 輸入參數：
   - document_id: `36c37289-3816-40cc-98cd-d697c71394d4`
   - version_id: `29fcc98a-d346-41c7-8dc8-89897e964242`
4. 點擊 **"Execute"**
5. 查看回應，應該顯示：
   - message: "已恢復到版本 1"
   - version_number: 1

**驗證恢復成功：**
- 再次執行**測試 1**，查看文件詳情
- current_version_id 應該變回 `29fcc98a-d346-41c7-8dc8-89897e964242`
- 內容應該是原始版本

**預期結果**: 成功恢復到版本 1，但版本歷史保留版本 2

---

### 測試 7: 刪除文件

**API**: `DELETE /api/doc/{document_id}`

⚠️ **注意：這會永久刪除文件及所有版本！**

1. 找到 `DELETE /api/doc/{document_id}`
2. 點擊 **"Try it out"**
3. 輸入 document_id：
   ```
   36c37289-3816-40cc-98cd-d697c71394d4
   ```
4. 點擊 **"Execute"**
5. 查看回應，應該顯示：
   - message: "文件已成功刪除"

**驗證刪除成功：**
- 再次執行**測試 1**
- 應該返回 404 錯誤："找不到指定的文件"

**預期結果**: 文件及所有版本被永久刪除

---

## 測試重點說明

### 版本控制機制
- ✅ 每次更新文件會自動建立新版本
- ✅ 版本號自動遞增（1, 2, 3...）
- ✅ 如果內容未變更，不會建立新版本
- ✅ 恢復舊版本不會刪除新版本（僅更改 current_version_id）

### 錯誤處理測試
您也可以測試錯誤情境：

1. **不存在的 document_id**：
   - 使用隨機 UUID（如 `00000000-0000-0000-0000-000000000000`）
   - 應該返回 404 錯誤

2. **不存在的 version_id**：
   - 使用錯誤的 version_id 恢復版本
   - 應該返回 404 錯誤

3. **重複更新相同內容**：
   - 連續兩次使用相同內容更新
   - 第二次應該返回 "內容未變更，未建立新版本"

---

## 前端整合測試

當您在前端頁面（http://localhost:3000/document/36c37289-3816-40cc-98cd-d697c71394d4）時：

1. **查看文件資訊**：
   - 標題
   - 版本數
   - 品質分數
   - 最後更新時間
   - 完整 Markdown 內容

2. **檢查前端 API 呼叫**：
   - 打開瀏覽器開發者工具（F12）
   - 切換到 Network 標籤
   - 重新整理頁面
   - 查看對 `/api/doc/{document_id}` 的請求和回應

---

## 下一步建議

完成基本測試後，您可以：

1. **建立多個版本**：連續更新 3-5 次，測試版本管理
2. **測試版本恢復**：在不同版本間切換
3. **測試前端顯示**：觀察前端如何顯示更新後的內容
4. **壓力測試**：建立大量版本，測試性能

---

## 需要幫助？

如果在測試過程中遇到任何問題：
- 檢查後端 server 日誌
- 查看 Swagger UI 的回應狀態碼
- 確認 document_id 和 version_id 正確

測試愉快！
