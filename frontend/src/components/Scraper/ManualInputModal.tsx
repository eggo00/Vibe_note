/**
 * 手動貼上內容 Modal
 * 爬蟲失敗時的 fallback 方案
 * 對應 tasks.md T041
 */
import React, { useState } from 'react';

export interface ManualInputModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (content: string) => void;
}

const ManualInputModal: React.FC<ManualInputModalProps> = ({
  isOpen,
  onClose,
  onSubmit
}) => {
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      setError('請輸入內容');
      return;
    }

    if (content.trim().length < 50) {
      setError('內容過短，請至少輸入 50 個字元');
      return;
    }

    setError(null);
    onSubmit(content);
    setContent('');
    onClose();
  };

  const handleClose = () => {
    setContent('');
    setError(null);
    onClose();
  };

  return (
    <>
      <div className="modal-overlay" onClick={handleClose} />
      <div className="modal-container" role="dialog" aria-modal="true">
        <div className="modal-header">
          <h2>手動貼上內容</h2>
          <button
            className="close-button"
            onClick={handleClose}
            aria-label="關閉"
          >
            ×
          </button>
        </div>

        <div className="modal-body">
          <p className="description">
            爬蟲無法存取該頁面？沒關係！您可以直接複製貼上內容到這裡。
          </p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="manual-content">
                內容 <span className="required">*</span>
              </label>

              <textarea
                id="manual-content"
                value={content}
                onChange={(e) => {
                  setContent(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="請貼上 Notion 頁面內容、程式碼、筆記等..."
                rows={12}
                className={error ? 'error' : ''}
              />

              {error && (
                <div className="error-message" role="alert">
                  {error}
                </div>
              )}

              <div className="hint">
                支援 Markdown 格式。至少 50 字元。
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                onClick={handleClose}
                className="button button-secondary"
              >
                取消
              </button>
              <button
                type="submit"
                className="button button-primary"
                disabled={!content.trim()}
              >
                提交內容
              </button>
            </div>
          </form>
        </div>
      </div>

      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          z-index: 1000;
        }

        .modal-container {
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 90%;
          max-width: 700px;
          max-height: 90vh;
          background: white;
          border-radius: 12px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
          z-index: 1001;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid #e5e7eb;
        }

        .modal-header h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #1a1a1a;
        }

        .close-button {
          width: 32px;
          height: 32px;
          border: none;
          background: transparent;
          font-size: 2rem;
          line-height: 1;
          color: #6b7280;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .close-button:hover {
          background-color: #f3f4f6;
        }

        .modal-body {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
        }

        .description {
          margin: 0 0 1.5rem 0;
          color: #6b7280;
          font-size: 0.95rem;
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

        textarea {
          padding: 0.75rem;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
          font-family: inherit;
          resize: vertical;
          transition: border-color 0.2s;
        }

        textarea:focus {
          outline: none;
          border-color: #3b82f6;
        }

        textarea.error {
          border-color: #ef4444;
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

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          padding: 1.5rem;
          border-top: 1px solid #e5e7eb;
        }

        .button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .button-secondary {
          background-color: white;
          color: #374151;
          border: 1px solid #d1d5db;
        }

        .button-secondary:hover {
          background-color: #f9fafb;
        }

        .button-primary {
          background-color: #3b82f6;
          color: white;
        }

        .button-primary:hover:not(:disabled) {
          background-color: #2563eb;
        }

        .button-primary:disabled {
          background-color: #9ca3af;
          cursor: not-allowed;
        }
      `}</style>
    </>
  );
};

export default ManualInputModal;
