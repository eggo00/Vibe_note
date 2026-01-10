/**
 * 資料來源輸入元件
 * 支援 Notion URL 輸入
 * 對應 tasks.md T039
 */
import React, { useState } from 'react';

export interface DataSourceInputProps {
  onSubmit: (url: string) => void;
  loading?: boolean;
}

const DataSourceInput: React.FC<DataSourceInputProps> = ({ onSubmit, loading = false }) => {
  const [notionUrl, setNotionUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  const validateNotionUrl = (url: string): boolean => {
    if (!url.trim()) {
      setError('請輸入 Notion 頁面 URL');
      return false;
    }

    // 驗證 Notion URL 格式
    const notionUrlPattern = /^https?:\/\/(www\.)?notion\.(so|site)\/.+/i;
    if (!notionUrlPattern.test(url)) {
      setError('請輸入有效的 Notion 公開頁面 URL（如：https://notion.so/...）');
      return false;
    }

    setError(null);
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateNotionUrl(notionUrl)) {
      onSubmit(notionUrl);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNotionUrl(e.target.value);
    if (error) {
      setError(null);
    }
  };

  return (
    <div className="data-source-input">
      <h2>輸入資料來源</h2>

      <form onSubmit={handleSubmit} className="input-form">
        <div className="form-group">
          <label htmlFor="notion-url">
            Notion 公開頁面 URL
            <span className="required">*</span>
          </label>

          <input
            id="notion-url"
            type="text"
            value={notionUrl}
            onChange={handleUrlChange}
            placeholder="https://notion.so/your-page-url"
            disabled={loading}
            className={error ? 'error' : ''}
          />

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <div className="hint">
            請確保 Notion 頁面已設定為「公開分享」
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !notionUrl.trim()}
          className="submit-button"
        >
          {loading ? '處理中...' : '開始分析'}
        </button>
      </form>

      <style jsx>{`
        .data-source-input {
          max-width: 600px;
          margin: 0 auto;
          padding: 2rem;
        }

        h2 {
          font-size: 1.5rem;
          margin-bottom: 1.5rem;
          color: #1a1a1a;
        }

        .input-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        label {
          font-weight: 500;
          color: #333;
          font-size: 0.95rem;
        }

        .required {
          color: #ef4444;
          margin-left: 0.25rem;
        }

        input[type="text"] {
          padding: 0.75rem;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        input[type="text"]:focus {
          outline: none;
          border-color: #3b82f6;
        }

        input[type="text"].error {
          border-color: #ef4444;
        }

        input[type="text"]:disabled {
          background-color: #f9fafb;
          cursor: not-allowed;
        }

        .error-message {
          color: #ef4444;
          font-size: 0.875rem;
          padding: 0.5rem;
          background-color: #fee2e2;
          border-radius: 4px;
        }

        .hint {
          color: #6b7280;
          font-size: 0.875rem;
        }

        .submit-button {
          padding: 0.875rem 1.5rem;
          background-color: #3b82f6;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .submit-button:hover:not(:disabled) {
          background-color: #2563eb;
        }

        .submit-button:disabled {
          background-color: #9ca3af;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default DataSourceInput;
