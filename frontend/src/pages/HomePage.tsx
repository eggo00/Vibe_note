/**
 * 首頁
 * 整合資料輸入、進度顯示與筆記生成流程
 * 對應 tasks.md T038
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DataSourceInput from '../components/Scraper/DataSourceInput';
import ScraperProgress, { ProgressStep } from '../components/Scraper/ScraperProgress';
import ManualInputModal from '../components/Scraper/ManualInputModal';
import { importAndAnalyze } from '../services/scraperService';
import { analyzeAndGenerate } from '../services/documentService';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  // 狀態管理
  const [step, setStep] = useState<ProgressStep>('idle');
  const [currentStep, setCurrentStep] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    blocksCount?: number;
    highQualityBlocks?: number;
    averageScore?: number;
  } | null>(null);
  const [showManualInput, setShowManualInput] = useState(false);
  const [sourceId, setSourceId] = useState<string | null>(null);

  /**
   * 處理 Notion URL 提交
   */
  const handleNotionSubmit = async (url: string) => {
    try {
      setStep('importing');
      setError(null);
      setResult(null);

      // Step 1 & 2: 匯入 + 分析
      const { sourceId: newSourceId, analyzeResult } = await importAndAnalyze(
        url,
        (stepMsg, prog) => {
          setCurrentStep(stepMsg);
          setProgress(prog);
          if (prog >= 50) {
            setStep('analyzing');
          }
        }
      );

      setSourceId(newSourceId);
      setResult({
        blocksCount: analyzeResult.total_blocks,
        highQualityBlocks: analyzeResult.high_quality_blocks,
        averageScore: analyzeResult.average_score
      });

      // 檢查是否有高品質內容
      if (analyzeResult.high_quality_blocks === 0) {
        setError('未找到高品質內容區塊，請嘗試其他資料來源或手動貼上內容');
        setStep('error');
        return;
      }

      // Step 3: 生成筆記
      setStep('generating');
      setCurrentStep('正在生成筆記...');
      setProgress(75);

      const generateResult = await analyzeAndGenerate(newSourceId);

      setProgress(100);
      setStep('completed');

      // 導向文件頁面
      setTimeout(() => {
        navigate(`/document/${generateResult.document_id}`);
      }, 1500);

    } catch (err: any) {
      console.error('處理失敗:', err);

      // 解析錯誤訊息
      let errorMessage = '處理失敗，請稍後再試';
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setStep('error');

      // 如果是爬蟲相關錯誤，顯示手動輸入選項
      if (errorMessage.includes('robots.txt') ||
          errorMessage.includes('403') ||
          errorMessage.includes('404')) {
        // 延遲顯示，給用戶時間看錯誤訊息
        setTimeout(() => {
          // 可以在這裡添加一個提示按鈕
        }, 2000);
      }
    }
  };

  /**
   * 處理手動貼上內容
   */
  const handleManualInput = async (content: string) => {
    // TODO: 實作手動內容處理 (Phase 4)
    console.log('手動內容:', content);
    alert('手動內容處理功能將在 Phase 4 實作');
  };

  /**
   * 重置狀態
   */
  const handleReset = () => {
    setStep('idle');
    setCurrentStep('');
    setProgress(0);
    setError(null);
    setResult(null);
    setSourceId(null);
  };

  return (
    <div className="home-page">
      <header className="page-header">
        <h1>🎓 Vibe Note AI 學霸筆記生成器</h1>
        <p className="subtitle">
          從 Notion 作業自動產生結構化技術筆記
        </p>
      </header>

      <main className="page-content">
        {step === 'idle' && (
          <DataSourceInput
            onSubmit={handleNotionSubmit}
            loading={false}
          />
        )}

        {step !== 'idle' && (
          <>
            <ScraperProgress
              step={step}
              currentStep={currentStep}
              progress={progress}
              error={error}
              result={result || undefined}
            />

            {step === 'error' && (
              <div className="action-buttons">
                <button
                  onClick={() => setShowManualInput(true)}
                  className="button button-secondary"
                >
                  手動貼上內容
                </button>
                <button
                  onClick={handleReset}
                  className="button button-primary"
                >
                  重新開始
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <ManualInputModal
        isOpen={showManualInput}
        onClose={() => setShowManualInput(false)}
        onSubmit={handleManualInput}
      />

      <style jsx>{`
        .home-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 2rem;
        }

        .page-header {
          text-align: center;
          margin-bottom: 3rem;
          color: white;
        }

        .page-header h1 {
          font-size: 2.5rem;
          margin: 0 0 0.5rem 0;
          font-weight: 700;
        }

        .subtitle {
          font-size: 1.125rem;
          margin: 0;
          opacity: 0.95;
        }

        .page-content {
          max-width: 800px;
          margin: 0 auto;
        }

        .action-buttons {
          display: flex;
          justify-content: center;
          gap: 1rem;
          margin-top: 2rem;
        }

        .button {
          padding: 0.875rem 1.75rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .button-primary {
          background-color: #3b82f6;
          color: white;
        }

        .button-primary:hover {
          background-color: #2563eb;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        .button-secondary {
          background-color: white;
          color: #374151;
          border: 2px solid #d1d5db;
        }

        .button-secondary:hover {
          background-color: #f9fafb;
          border-color: #9ca3af;
        }

        @media (max-width: 768px) {
          .page-header h1 {
            font-size: 1.875rem;
          }

          .subtitle {
            font-size: 1rem;
          }

          .action-buttons {
            flex-direction: column;
          }

          .button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default HomePage;
