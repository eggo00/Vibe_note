/**
 * React App 入口
 * 設定路由與全域狀態
 * 對應 tasks.md T024
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import TestPage from './pages/TestPage';

// 頁面元件（目前使用 placeholder）
const HomePage: React.FC = () => (
  <div style={{ padding: '20px' }}>
    <h1>Vibe Note - AI 學霸筆記生成器</h1>
    <p>歡迎使用 Vibe Coding AI 筆記生成系統</p>
    <div style={{ marginTop: '20px' }}>
      <h2>功能導覽</h2>
      <ul>
        <li>📝 從 Notion 作業生成筆記草稿</li>
        <li>🎨 學習老師寫作風格並應用</li>
        <li>✏️ 線上編輯與版本管理</li>
        <li>📤 匯出多種格式繳交作業</li>
        <li>🔍 從 GitHub Repo 提取專案資訊</li>
      </ul>
    </div>
    <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#fff', borderRadius: '8px' }}>
      <h3>🧪 開發工具</h3>
      <Link to="/test" style={{ color: '#007bff', textDecoration: 'underline' }}>
        前後端串接測試頁面
      </Link>
    </div>
  </div>
);

const NotFoundPage: React.FC = () => (
  <div style={{ padding: '20px', textAlign: 'center' }}>
    <h1>404 - 頁面不存在</h1>
    <p>找不到您要的頁面</p>
    <a href="/" style={{ color: '#007bff' }}>返回首頁</a>
  </div>
);

/**
 * App 主元件
 */
const App: React.FC = () => {
  return (
    <Router>
      <div className="app" style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <Routes>
          {/* 首頁 */}
          <Route path="/" element={<HomePage />} />

          {/* 測試頁面 */}
          <Route path="/test" element={<TestPage />} />

          {/* 未來路由（Phase 3 實作） */}
          {/* <Route path="/scraper" element={<ScraperPage />} /> */}
          {/* <Route path="/editor/:documentId" element={<EditorPage />} /> */}
          {/* <Route path="/export/:documentId" element={<ExportPage />} /> */}

          {/* 404 頁面 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
