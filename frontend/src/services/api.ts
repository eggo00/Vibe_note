/**
 * API Client 模組
 * 統一管理所有 API 請求，處理錯誤與認證
 * 對應 tasks.md T025
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// API 錯誤回應格式
export interface ApiErrorResponse {
  error: string;
  code: string;
  details?: Record<string, any>;
}

// API 成功回應格式
export interface ApiSuccessResponse<T = any> {
  success: boolean;
  data: T;
}

// API Client 類別
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    this.client = axios.create({
      baseURL,
      timeout: 30000, // 30 秒超時
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 請求攔截器
    this.client.interceptors.request.use(
      (config) => {
        // 可以在這裡加入認證 token（未來擴充）
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 回應攔截器（統一錯誤處理）
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorResponse>) => {
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * 統一錯誤處理
   */
  private handleError(error: AxiosError<ApiErrorResponse>): Error {
    if (error.response) {
      // 伺服器回應錯誤（4xx, 5xx）
      const { data, status } = error.response;

      if (data && data.error) {
        // 使用 API 回傳的錯誤訊息
        const errorMessage = `[${data.code || 'API_ERROR'}] ${data.error}`;
        const apiError = new Error(errorMessage) as any;
        apiError.code = data.code;
        apiError.details = data.details;
        apiError.status = status;
        return apiError;
      }

      // 沒有錯誤訊息時使用預設訊息
      return new Error(`HTTP ${status}: ${error.message}`);
    } else if (error.request) {
      // 請求已發送但沒有收到回應（網路問題）
      return new Error('無法連線到伺服器，請檢查網路連線');
    } else {
      // 其他錯誤
      return new Error(error.message || '未知錯誤');
    }
  }

  /**
   * GET 請求
   */
  async get<T = any>(url: string, params?: Record<string, any>): Promise<T> {
    const response = await this.client.get<ApiSuccessResponse<T>>(url, { params });
    return response.data.data;
  }

  /**
   * POST 請求
   */
  async post<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<ApiSuccessResponse<T>>(url, data);
    return response.data.data;
  }

  /**
   * PUT 請求
   */
  async put<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<ApiSuccessResponse<T>>(url, data);
    return response.data.data;
  }

  /**
   * DELETE 請求
   */
  async delete<T = any>(url: string): Promise<T> {
    const response = await this.client.delete<ApiSuccessResponse<T>>(url);
    return response.data.data;
  }

  /**
   * 健康檢查
   */
  async healthCheck(): Promise<{ status: string; database: string; timestamp: number; environment: string }> {
    return this.get('/health');
  }

  /**
   * 取得原始 Axios instance（需要更細緻控制時使用）
   */
  getClient(): AxiosInstance {
    return this.client;
  }
}

// 匯出單例
export const apiClient = new ApiClient();

// 匯出預設實例
export default apiClient;
