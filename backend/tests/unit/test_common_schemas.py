"""
API 統一回應格式測試
驗證 ErrorResponse 和 SuccessResponse 符合憲法規範
"""
import pytest
from src.schemas.common import (
    ErrorResponse,
    SuccessResponse,
    ErrorCode,
    create_error_response,
    create_success_response,
    error_dict,
    success_dict
)


class TestErrorResponse:
    """ErrorResponse 測試"""

    def test_create_basic_error(self):
        """正常情境：建立基本錯誤回應"""
        error = ErrorResponse(
            error="文件不存在",
            code="DOCUMENT_NOT_FOUND"
        )

        assert error.error == "文件不存在"
        assert error.code == "DOCUMENT_NOT_FOUND"
        assert error.details is None

    def test_create_error_with_details(self):
        """正常情境：建立包含細節的錯誤回應"""
        error = ErrorResponse(
            error="爬蟲失敗",
            code="NOTION_SCRAPE_FAILED",
            details={"url": "https://notion.so/test", "status_code": 404}
        )

        assert error.error == "爬蟲失敗"
        assert error.code == "NOTION_SCRAPE_FAILED"
        assert error.details == {"url": "https://notion.so/test", "status_code": 404}

    def test_error_response_to_dict(self):
        """正常情境：轉換為 dict"""
        error = ErrorResponse(
            error="測試錯誤",
            code="TEST_ERROR",
            details={"key": "value"}
        )

        error_dict = error.model_dump()

        assert error_dict == {
            "error": "測試錯誤",
            "code": "TEST_ERROR",
            "details": {"key": "value"}
        }

    def test_error_response_json(self):
        """正常情境：轉換為 JSON"""
        error = ErrorResponse(
            error="測試",
            code="TEST"
        )

        json_str = error.model_dump_json()

        assert "測試" in json_str
        assert "TEST" in json_str


class TestSuccessResponse:
    """SuccessResponse 測試"""

    def test_create_success_with_dict(self):
        """正常情境：建立成功回應（dict 資料）"""
        response = SuccessResponse(
            success=True,
            data={"document_id": "123", "title": "測試筆記"}
        )

        assert response.success is True
        assert response.data == {"document_id": "123", "title": "測試筆記"}

    def test_create_success_with_list(self):
        """正常情境：建立成功回應（list 資料）"""
        response = SuccessResponse(
            success=True,
            data=[{"id": "1"}, {"id": "2"}]
        )

        assert response.success is True
        assert len(response.data) == 2

    def test_create_success_with_string(self):
        """正常情境：建立成功回應（string 資料）"""
        response = SuccessResponse(
            success=True,
            data="操作成功"
        )

        assert response.success is True
        assert response.data == "操作成功"

    def test_success_default_value(self):
        """正常情境：success 預設為 True"""
        response = SuccessResponse(data={"test": "data"})

        assert response.success is True

    def test_success_response_to_dict(self):
        """正常情境：轉換為 dict"""
        response = SuccessResponse(
            data={"user_id": 123, "name": "Alice"}
        )

        response_dict = response.model_dump()

        assert response_dict == {
            "success": True,
            "data": {"user_id": 123, "name": "Alice"}
        }


class TestErrorCode:
    """ErrorCode 常數測試"""

    def test_error_codes_defined(self):
        """正常情境：驗證錯誤代碼已定義"""
        assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"
        assert ErrorCode.DOCUMENT_NOT_FOUND == "DOCUMENT_NOT_FOUND"
        assert ErrorCode.NOTION_SCRAPE_FAILED == "NOTION_SCRAPE_FAILED"
        assert ErrorCode.GENERATION_FAILED == "GENERATION_FAILED"

    def test_error_codes_uppercase(self):
        """規範驗證：所有錯誤代碼應為大寫"""
        import inspect

        for name, value in inspect.getmembers(ErrorCode):
            if not name.startswith('_') and isinstance(value, str):
                assert value.isupper(), f"錯誤代碼 {name} 應為大寫"
                assert value == value.replace(' ', '_'), f"錯誤代碼 {name} 應使用底線"


class TestHelperFunctions:
    """Helper functions 測試"""

    def test_create_error_response(self):
        """正常情境：使用 helper 建立錯誤回應"""
        error = create_error_response(
            "文件不存在",
            ErrorCode.DOCUMENT_NOT_FOUND,
            {"document_id": "abc"}
        )

        assert isinstance(error, ErrorResponse)
        assert error.error == "文件不存在"
        assert error.code == "DOCUMENT_NOT_FOUND"
        assert error.details == {"document_id": "abc"}

    def test_create_error_response_default_code(self):
        """正常情境：預設錯誤代碼為 INTERNAL_ERROR"""
        error = create_error_response("未知錯誤")

        assert error.code == ErrorCode.INTERNAL_ERROR

    def test_create_error_response_without_details(self):
        """正常情境：不提供 details"""
        error = create_error_response(
            "操作失敗",
            ErrorCode.VALIDATION_ERROR
        )

        assert error.details is None

    def test_create_success_response(self):
        """正常情境：使用 helper 建立成功回應"""
        response = create_success_response({"id": "123", "status": "ok"})

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.data == {"id": "123", "status": "ok"}

    def test_error_dict_helper(self):
        """正常情境：使用 error_dict helper"""
        result = error_dict(
            "爬蟲失敗",
            ErrorCode.SCRAPE_FAILED,
            {"url": "https://test.com"}
        )

        assert result == {
            "error": "爬蟲失敗",
            "code": "SCRAPE_FAILED",
            "details": {"url": "https://test.com"}
        }

    def test_error_dict_without_details(self):
        """正常情境：error_dict 不包含 details"""
        result = error_dict("錯誤訊息", ErrorCode.NOT_FOUND)

        assert result == {
            "error": "錯誤訊息",
            "code": "NOT_FOUND"
        }
        assert "details" not in result

    def test_success_dict_helper(self):
        """正常情境：使用 success_dict helper"""
        result = success_dict({"user": "Alice", "age": 30})

        assert result == {
            "success": True,
            "data": {"user": "Alice", "age": 30}
        }


class TestConstitutionCompliance:
    """憲法規範符合性測試"""

    def test_error_format_matches_constitution(self):
        """規範驗證：錯誤格式符合憲法規定"""
        # 憲法規定：{"error": "描述", "code": "ERROR_CODE"}
        error = create_error_response("測試錯誤", "TEST_CODE")
        error_data = error.model_dump()

        assert "error" in error_data
        assert "code" in error_data
        assert isinstance(error_data["error"], str)
        assert isinstance(error_data["code"], str)

    def test_success_format_matches_constitution(self):
        """規範驗證：成功格式符合憲法規定"""
        # 憲法規定：{"success": true, "data": {...}}
        response = create_success_response({"test": "data"})
        response_data = response.model_dump()

        assert "success" in response_data
        assert "data" in response_data
        assert response_data["success"] is True

    def test_error_code_uppercase_with_underscore(self):
        """規範驗證：錯誤代碼格式（全大寫 + 底線）"""
        error = create_error_response(
            "測試",
            ErrorCode.DOCUMENT_NOT_FOUND
        )

        assert error.code == error.code.upper()
        assert ' ' not in error.code


class TestRealWorldUsage:
    """真實使用場景測試"""

    def test_api_error_scenario(self):
        """真實場景：API 錯誤回應"""
        # 模擬 API 端點返回錯誤
        error = create_error_response(
            "無法爬取 Notion 頁面，請確認 URL 是否正確",
            ErrorCode.NOTION_SCRAPE_FAILED,
            {"url": "https://notion.so/invalid", "status_code": 404}
        )

        assert "Notion" in error.error
        assert error.code == "NOTION_SCRAPE_FAILED"
        assert error.details["status_code"] == 404

    def test_api_success_scenario(self):
        """真實場景：API 成功回應"""
        # 模擬創建文件成功
        response = create_success_response({
            "document_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "React Hooks 筆記",
            "created_at": "2026-01-08T10:30:00Z"
        })

        assert response.success is True
        assert "document_id" in response.data
        assert "title" in response.data

    def test_chinese_error_message(self):
        """真實場景：中文錯誤訊息"""
        error = create_error_response(
            "生成的筆記與來源內容相似度過高（> 0.7），請調整生成策略",
            ErrorCode.GENERATION_TOO_SIMILAR,
            {"max_similarity": 0.85}
        )

        assert "相似度" in error.error
        assert error.details["max_similarity"] == 0.85

    def test_json_serialization(self):
        """真實場景：JSON 序列化"""
        response = create_success_response({
            "blocks": [
                {"id": "1", "type": "heading", "score": 85.5},
                {"id": "2", "type": "code", "score": 92.3}
            ]
        })

        json_str = response.model_dump_json()

        assert "blocks" in json_str
        assert "85.5" in json_str
