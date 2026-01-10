/**
 * 文件頁面
 * 顯示生成的筆記內容與版本歷史
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getDocument, type DocumentResponse } from '../services/documentService';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import ErrorMessage from '../components/Common/ErrorMessage';

const DocumentPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError('無效的文件 ID');
      setLoading(false);
      return;
    }

    loadDocument();
  }, [id]);

  const loadDocument = async () => {
    try {
      setLoading(true);
      setError(null);
      const doc = await getDocument(id!);
      setDocument(doc);
    } catch (err: any) {
      console.error('載入文件失敗:', err);
      setError(err.response?.data?.error || '載入文件失敗');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="載入筆記中..." />;
  }

  if (error) {
    return (
      <div className="document-page">
        <ErrorMessage message={error} />
        <div className="actions">
          <button onClick={() => navigate('/')} className="button">
            返回首頁
          </button>
        </div>
      </div>
    );
  }

  if (!document) {
    return null;
  }

  return (
    <div className="document-page">
      <header className="document-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← 返回
        </button>

        <div className="header-info">
          <h1>{document.title}</h1>
          <div className="meta">
            <span>版本數: {document.version_count}</span>
            {document.aggregate_score && (
              <span>品質分數: {document.aggregate_score.toFixed(1)}</span>
            )}
            <span>
              最後更新: {new Date(document.updated_at).toLocaleDateString('zh-TW')}
            </span>
          </div>
        </div>
      </header>

      <main className="document-content">
        <div className="markdown-content">
          <pre>{document.content}</pre>
        </div>
      </main>

      <style jsx>{`
        .document-page {
          min-height: 100vh;
          background-color: #f9fafb;
        }

        .document-header {
          background: white;
          padding: 1.5rem 2rem;
          border-bottom: 1px solid #e5e7eb;
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .back-button {
          background: none;
          border: none;
          color: #3b82f6;
          font-size: 1rem;
          cursor: pointer;
          padding: 0.5rem 0;
          margin-bottom: 1rem;
          transition: color 0.2s;
        }

        .back-button:hover {
          color: #2563eb;
        }

        .header-info h1 {
          font-size: 2rem;
          margin: 0 0 0.75rem 0;
          color: #1a1a1a;
        }

        .meta {
          display: flex;
          gap: 1.5rem;
          color: #6b7280;
          font-size: 0.875rem;
        }

        .document-content {
          max-width: 900px;
          margin: 2rem auto;
          padding: 0 2rem;
        }

        .markdown-content {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .markdown-content pre {
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: 'Georgia', serif;
          font-size: 1.05rem;
          line-height: 1.7;
          color: #1a1a1a;
          margin: 0;
        }

        .actions {
          text-align: center;
          padding: 2rem;
        }

        .button {
          padding: 0.875rem 1.75rem;
          background-color: #3b82f6;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .button:hover {
          background-color: #2563eb;
        }

        @media (max-width: 768px) {
          .document-header {
            padding: 1rem;
          }

          .header-info h1 {
            font-size: 1.5rem;
          }

          .meta {
            flex-direction: column;
            gap: 0.5rem;
          }

          .document-content {
            padding: 0 1rem;
          }

          .markdown-content {
            padding: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentPage;
