/**
 * 爬蟲服務
 * 處理資料來源匯入與內容分析
 * 對應 tasks.md T042
 */
import apiClient from './api';

export interface NotionImportRequest {
  url: string;
  document_id?: string;
}

export interface NotionImportResponse {
  source_id: string;
  url: string;
  blocks_count: number;
  robots_allowed: boolean;
  fetched_at: string;
}

export interface AnalyzeRequest {
  source_id: string;
}

export interface AnalyzeResponse {
  source_id: string;
  total_blocks: number;
  high_quality_blocks: number;
  average_score: number;
  threshold: number;
  blocks: Array<{
    block_id: string;
    score: number;
    reasoning: string;
    is_high_quality: boolean;
  }>;
}

export interface AnalysisStatsResponse {
  source_id: string;
  url: string;
  total_blocks: number;
  high_quality_blocks: number;
  average_score: number;
  threshold: number;
  block_type_distribution: Record<string, number>;
  score_distribution: Record<string, number>;
}

/**
 * 匯入 Notion 頁面
 */
export const importNotionPage = async (
  request: NotionImportRequest
): Promise<NotionImportResponse> => {
  return apiClient.post<NotionImportResponse>('/api/notion/import', request);
};

/**
 * 分析內容品質
 */
export const analyzeContent = async (
  request: AnalyzeRequest
): Promise<AnalyzeResponse> => {
  return apiClient.post<AnalyzeResponse>('/api/analyze', request);
};

/**
 * 取得分析統計
 */
export const getAnalysisStats = async (
  sourceId: string
): Promise<AnalysisStatsResponse> => {
  return apiClient.get<AnalysisStatsResponse>(`/api/analyze/source/${sourceId}/stats`);
};

/**
 * 完整流程：匯入 + 分析
 *
 * @param notionUrl - Notion 公開頁面 URL
 * @param onProgress - 進度回調
 * @returns 分析結果
 */
export const importAndAnalyze = async (
  notionUrl: string,
  onProgress?: (step: string, progress: number) => void
): Promise<{
  sourceId: string;
  analyzeResult: AnalyzeResponse;
}> => {
  try {
    // Step 1: 匯入 Notion 頁面
    onProgress?.('正在爬取 Notion 頁面...', 25);
    const importResult = await importNotionPage({ url: notionUrl });

    // Step 2: 分析內容品質
    onProgress?.('正在分析內容品質...', 50);
    const analyzeResult = await analyzeContent({ source_id: importResult.source_id });

    onProgress?.('分析完成', 100);

    return {
      sourceId: importResult.source_id,
      analyzeResult
    };
  } catch (error) {
    console.error('匯入與分析失敗:', error);
    throw error;
  }
};

export default {
  importNotionPage,
  analyzeContent,
  getAnalysisStats,
  importAndAnalyze
};
