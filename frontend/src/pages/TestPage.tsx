/**
 * 測試頁面
 * 驗證前後端串接與通用元件
 */
import React, { useState } from 'react';
import apiClient from '../services/api';
import ErrorMessage from '../components/Common/ErrorMessage';
import LoadingSpinner from '../components/Common/LoadingSpinner';

interface HealthData {
  status: string;
  database: string;
  timestamp: number;
  environment: string;
}

export const TestPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthData, setHealthData] = useState<HealthData | null>(null);

  const testApiConnection = async () => {
    setLoading(true);
    setError(null);
    setHealthData(null);

    try {
      const data = await apiClient.healthCheck();
      setHealthData(data);
    } catch (err: any) {
      setError(err.message || '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧪 前後端串接測試</h1>
      <p style={{ marginTop: '8px', color: '#666' }}>
        測試前端與後端 API 的連線狀態
      </p>

      <div style={{ marginTop: '30px' }}>
        <button
          onClick={testApiConnection}
          disabled={loading}
          style={{
            padding: '10px 20px',
            fontSize: '1rem',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? '測試中...' : '測試 API 連線'}
        </button>
      </div>

      {/* 載入動畫 */}
      {loading && (
        <div style={{ marginTop: '30px' }}>
          <LoadingSpinner message="正在連線到後端 API..." size="medium" />
        </div>
      )}

      {/* 錯誤訊息 */}
      {error && (
        <div style={{ marginTop: '30px' }}>
          <ErrorMessage
            message={error}
            code="API_ERROR"
            dismissible
            onDismiss={() => setError(null)}
          />
        </div>
      )}

      {/* 成功結果 */}
      {healthData && !loading && (
        <div
          style={{
            marginTop: '30px',
            padding: '20px',
            backgroundColor: '#d4edda',
            border: '1px solid #c3e6cb',
            borderRadius: '4px',
            color: '#155724',
          }}
        >
          <h3 style={{ marginBottom: '12px' }}>✅ 連線成功</h3>
          <div style={{ fontSize: '0.95rem' }}>
            <p><strong>狀態:</strong> {healthData.status}</p>
            <p><strong>資料庫:</strong> {healthData.database}</p>
            <p><strong>環境:</strong> {healthData.environment}</p>
            <p><strong>時間戳:</strong> {new Date(healthData.timestamp * 1000).toLocaleString()}</p>
          </div>
        </div>
      )}

      {/* 元件展示區 */}
      <div style={{ marginTop: '50px', paddingTop: '30px', borderTop: '1px solid #ddd' }}>
        <h2>📦 通用元件展示</h2>

        <div style={{ marginTop: '20px' }}>
          <h3>LoadingSpinner 元件</h3>
          <div style={{ display: 'flex', gap: '30px', marginTop: '15px' }}>
            <div>
              <p style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#666' }}>Small</p>
              <LoadingSpinner size="small" message="載入中..." />
            </div>
            <div>
              <p style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#666' }}>Medium</p>
              <LoadingSpinner size="medium" message="處理中..." />
            </div>
            <div>
              <p style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#666' }}>Large</p>
              <LoadingSpinner size="large" message="生成筆記中..." />
            </div>
          </div>
        </div>

        <div style={{ marginTop: '30px' }}>
          <h3>ErrorMessage 元件</h3>
          <div style={{ marginTop: '15px' }}>
            <ErrorMessage
              message="這是一個測試錯誤訊息"
              code="TEST_ERROR"
              dismissible
              onDismiss={() => alert('錯誤訊息已關閉')}
            />
            <ErrorMessage
              message="無法連線到伺服器，請檢查網路連線"
              code="NETWORK_ERROR"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestPage;
