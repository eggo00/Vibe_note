/**
 * 爬取進度顯示元件
 * 顯示匯入和分析的進度狀態
 * 對應 tasks.md T040
 */
import React from 'react';

export type ProgressStep = 'idle' | 'importing' | 'analyzing' | 'generating' | 'completed' | 'error';

export interface ScraperProgressProps {
  step: ProgressStep;
  currentStep?: string;
  progress?: number;
  error?: string | null;
  result?: {
    blocksCount?: number;
    highQualityBlocks?: number;
    averageScore?: number;
  };
}

const ScraperProgress: React.FC<ScraperProgressProps> = ({
  step,
  currentStep,
  progress = 0,
  error,
  result
}) => {
  const getStepInfo = (currentStep: ProgressStep) => {
    switch (currentStep) {
      case 'importing':
        return {
          icon: '🔍',
          title: '正在爬取 Notion 頁面',
          description: '讀取頁面內容並解析區塊...'
        };
      case 'analyzing':
        return {
          icon: '🧠',
          title: '正在分析內容品質',
          description: 'AI 評分中，篩選高品質學習內容...'
        };
      case 'generating':
        return {
          icon: '✨',
          title: '正在生成筆記',
          description: '整理知識點並產出結構化筆記...'
        };
      case 'completed':
        return {
          icon: '✅',
          title: '完成！',
          description: '筆記已成功生成'
        };
      case 'error':
        return {
          icon: '❌',
          title: '處理失敗',
          description: error || '發生未知錯誤'
        };
      default:
        return {
          icon: '⏳',
          title: '準備中',
          description: '等待開始...'
        };
    }
  };

  const stepInfo = getStepInfo(step);
  const showProgressBar = step !== 'idle' && step !== 'error' && step !== 'completed';

  return (
    <div className="scraper-progress">
      <div className="progress-header">
        <div className="icon">{stepInfo.icon}</div>
        <div className="info">
          <h3>{stepInfo.title}</h3>
          <p>{currentStep || stepInfo.description}</p>
        </div>
      </div>

      {showProgressBar && (
        <div className="progress-bar-container">
          <div
            className="progress-bar"
            style={{ width: `${progress}%` }}
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      )}

      {step === 'completed' && result && (
        <div className="result-summary">
          <h4>分析結果</h4>
          <div className="stats">
            {result.blocksCount !== undefined && (
              <div className="stat-item">
                <span className="label">總區塊數：</span>
                <span className="value">{result.blocksCount}</span>
              </div>
            )}
            {result.highQualityBlocks !== undefined && (
              <div className="stat-item">
                <span className="label">高品質區塊：</span>
                <span className="value highlight">{result.highQualityBlocks}</span>
              </div>
            )}
            {result.averageScore !== undefined && (
              <div className="stat-item">
                <span className="label">平均分數：</span>
                <span className="value">{result.averageScore.toFixed(1)}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {step === 'error' && error && (
        <div className="error-details" role="alert">
          <p>{error}</p>
        </div>
      )}

      <style jsx>{`
        .scraper-progress {
          max-width: 600px;
          margin: 2rem auto;
          padding: 2rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .progress-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .icon {
          font-size: 2.5rem;
          flex-shrink: 0;
        }

        .info {
          flex: 1;
        }

        .info h3 {
          font-size: 1.25rem;
          margin: 0 0 0.5rem 0;
          color: #1a1a1a;
        }

        .info p {
          margin: 0;
          color: #6b7280;
          font-size: 0.95rem;
        }

        .progress-bar-container {
          width: 100%;
          height: 8px;
          background-color: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 1.5rem;
        }

        .progress-bar {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #2563eb);
          transition: width 0.3s ease;
        }

        .result-summary {
          margin-top: 1.5rem;
          padding: 1rem;
          background-color: #f0fdf4;
          border-radius: 8px;
          border: 1px solid #86efac;
        }

        .result-summary h4 {
          margin: 0 0 0.75rem 0;
          color: #166534;
          font-size: 1rem;
        }

        .stats {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .stat-item {
          display: flex;
          justify-content: space-between;
          font-size: 0.95rem;
        }

        .stat-item .label {
          color: #374151;
        }

        .stat-item .value {
          font-weight: 600;
          color: #1a1a1a;
        }

        .stat-item .value.highlight {
          color: #059669;
        }

        .error-details {
          margin-top: 1rem;
          padding: 1rem;
          background-color: #fee2e2;
          border-radius: 8px;
          border: 1px solid #fca5a5;
          color: #991b1b;
        }

        .error-details p {
          margin: 0;
        }
      `}</style>
    </div>
  );
};

export default ScraperProgress;
