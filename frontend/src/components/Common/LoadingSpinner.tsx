/**
 * LoadingSpinner 元件
 * 顯示載入動畫
 * 對應 tasks.md T027
 */
import React from 'react';

export interface LoadingSpinnerProps {
  /** 載入訊息 */
  message?: string;
  /** 尺寸（small, medium, large） */
  size?: 'small' | 'medium' | 'large';
  /** 是否置中顯示 */
  centered?: boolean;
  /** 額外的 CSS class */
  className?: string;
}

/**
 * LoadingSpinner 元件
 *
 * 使用範例：
 * ```tsx
 * <LoadingSpinner message="載入中..." size="medium" centered />
 * ```
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = '載入中...',
  size = 'medium',
  centered = false,
  className = '',
}) => {
  // 根據尺寸設定大小
  const sizeMap = {
    small: 20,
    medium: 40,
    large: 60,
  };

  const spinnerSize = sizeMap[size];

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px',
    ...(centered && {
      justifyContent: 'center',
      minHeight: '200px',
    }),
  };

  return (
    <div className={`loading-spinner ${className}`} style={containerStyle}>
      {/* 旋轉動畫 */}
      <div
        style={{
          width: spinnerSize,
          height: spinnerSize,
          border: `${spinnerSize / 10}px solid rgba(0, 0, 0, 0.1)`,
          borderTop: `${spinnerSize / 10}px solid #007bff`,
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />

      {/* 載入訊息 */}
      {message && (
        <div
          style={{
            fontSize: size === 'small' ? '0.875rem' : '1rem',
            color: '#666',
          }}
        >
          {message}
        </div>
      )}

      {/* CSS 動畫定義 */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
