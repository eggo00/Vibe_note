/**
 * React App 入口
 * 設定路由與全域狀態
 * 對應 tasks.md T024
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DocumentPage from './pages/DocumentPage';
import TestPage from './pages/TestPage';

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
          {/* 首頁 - 資料輸入與筆記生成 */}
          <Route path="/" element={<HomePage />} />

          {/* 文件頁面 - 顯示生成的筆記 */}
          <Route path="/document/:id" element={<DocumentPage />} />

          {/* 測試頁面 */}
          <Route path="/test" element={<TestPage />} />

          {/* 404 頁面 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
