/**
 * 文件服務
 * 處理筆記生成、文件管理與版本控制
 * 對應 tasks.md T043
 */
import apiClient from './api';

export interface GenerateRequest {
  source_id: string;
  project_context?: string;
  title?: string;
  use_custom_style?: boolean;
  style_profile_id?: string;
}

export interface GenerateResponse {
  document_id: string;
  version_id: string;
  title: string;
  content_preview: string;
  total_blocks_used: number;
  quality_score: number;
}

export interface DocumentResponse {
  document_id: string;
  title: string;
  content: string;
  current_version_id: string;
  aggregate_score: number | null;
  created_at: string;
  updated_at: string;
  version_count: number;
}

export interface VersionInfo {
  version_id: string;
  version_number: number;
  created_at: string;
  change_summary: string | null;
  content_preview: string;
}

export interface VersionsResponse {
  document_id: string;
  title: string;
  total_versions: number;
  versions: VersionInfo[];
}

export interface SpecificVersionResponse {
  version_id: string;
  version_number: number;
  document_id: string;
  content: string;
  created_at: string;
  change_summary: string | null;
  is_current: boolean;
}

export interface UpdateDocumentRequest {
  content: string;
  change_summary?: string;
}

export interface UpdateDocumentResponse {
  document_id: string;
  version_id: string;
  version_number: number;
  title: string;
  content_preview: string;
  change_summary: string;
}

/**
 * 生成筆記
 */
export const generateNote = async (
  request: GenerateRequest
): Promise<GenerateResponse> => {
  return apiClient.post<GenerateResponse>('/api/generate', request);
};

/**
 * 重新生成筆記
 */
export const regenerateNote = async (
  documentId: string,
  projectContext?: string
): Promise<{
  document_id: string;
  version_id: string;
  version_number: number;
  content_preview: string;
}> => {
  return apiClient.post(
    `/api/generate/regenerate/${documentId}`,
    null,
    { params: { project_context: projectContext } }
  );
};

/**
 * 取得文件詳情
 */
export const getDocument = async (
  documentId: string
): Promise<DocumentResponse> => {
  return apiClient.get<DocumentResponse>(`/api/doc/${documentId}`);
};

/**
 * 取得文件的所有版本
 */
export const getDocumentVersions = async (
  documentId: string
): Promise<VersionsResponse> => {
  return apiClient.get<VersionsResponse>(`/api/doc/${documentId}/versions`);
};

/**
 * 取得特定版本的內容
 */
export const getSpecificVersion = async (
  documentId: string,
  versionId: string
): Promise<SpecificVersionResponse> => {
  return apiClient.get<SpecificVersionResponse>(
    `/api/doc/${documentId}/version/${versionId}`
  );
};

/**
 * 更新文件內容
 */
export const updateDocument = async (
  documentId: string,
  request: UpdateDocumentRequest
): Promise<UpdateDocumentResponse> => {
  return apiClient.put<UpdateDocumentResponse>(
    `/api/doc/${documentId}`,
    request
  );
};

/**
 * 刪除文件
 */
export const deleteDocument = async (
  documentId: string
): Promise<{ message: string; document_id: string }> => {
  return apiClient.delete(`/api/doc/${documentId}`);
};

/**
 * 恢復到指定版本
 */
export const restoreVersion = async (
  documentId: string,
  versionId: string
): Promise<{
  message: string;
  document_id: string;
  version_id: string;
  version_number: number;
  content_preview: string;
}> => {
  return apiClient.post(`/api/doc/${documentId}/restore/${versionId}`);
};

/**
 * 完整流程：分析 + 生成筆記
 *
 * @param sourceId - 資料來源 ID
 * @param title - 筆記標題（選填）
 * @param projectContext - 專案背景（選填）
 * @returns 生成的文件 ID 和內容預覽
 */
export const analyzeAndGenerate = async (
  sourceId: string,
  title?: string,
  projectContext?: string
): Promise<GenerateResponse> => {
  return generateNote({
    source_id: sourceId,
    title,
    project_context: projectContext
  });
};

export default {
  generateNote,
  regenerateNote,
  getDocument,
  getDocumentVersions,
  getSpecificVersion,
  updateDocument,
  deleteDocument,
  restoreVersion,
  analyzeAndGenerate
};
