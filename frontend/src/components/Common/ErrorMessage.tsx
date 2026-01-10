/**
 * ErrorMessage 元件
 * 顯示統一格式的錯誤訊息
 * 對應 tasks.md T026
 */
import React from 'react';

export interface ErrorMessageProps {
  /** 錯誤訊息 */
  message: string;
  /** 錯誤代碼（可選） */
  code?: string;
  /** 是否可關閉 */
  dismissible?: boolean;
  /** 關閉回調 */
  onDismiss?: () => void;
  /** 額外的 CSS class */
  className?: string;
}

/**
 * ErrorMessage 元件
 *
 * 使用範例：
 * ```tsx
 * <ErrorMessage
 *   message="無法連線到伺服器"
 *   code="NETWORK_ERROR"
 *   dismissible
 *   onDismiss={() => setError(null)}
 * />
 * ```
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  code,
  dismissible = false,
  onDismiss,
  className = '',
}) => {
  return (
    <div
      className={`error-message ${className}`}
      role="alert"
      style={{
        padding: '12px 16px',
        backgroundColor: '#fee',
        border: '1px solid #fcc',
        borderRadius: '4px',
        color: '#c33',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, marginBottom: code ? '4px' : 0 }}>
          {message}
        </div>
        {code && (
          <div style={{ fontSize: '0.875rem', opacity: 0.8 }}>
            錯誤代碼: {code}
          </div>
        )}
      </div>

      {dismissible && onDismiss && (
        <button
          onClick={onDismiss}
          aria-label="關閉錯誤訊息"
          style={{
            marginLeft: '12px',
            padding: '4px 8px',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            fontSize: '1.25rem',
            color: '#c33',
            lineHeight: 1,
          }}
        >
          ×
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
