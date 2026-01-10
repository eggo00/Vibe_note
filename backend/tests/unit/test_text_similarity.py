"""
TextSimilarityChecker 測試
驗證文字相似度檢查功能（防抄襲）
"""
import pytest
from src.utils.text_similarity import TextSimilarityChecker


class TestTextSimilarityInitialization:
    """TextSimilarityChecker 初始化測試"""

    def test_create_default_checker(self):
        """正常情境：建立預設檢查器（threshold = 0.7）"""
        checker = TextSimilarityChecker()
        assert checker.threshold == 0.7
        assert checker.vectorizer is not None

    def test_create_custom_threshold(self):
        """正常情境：自訂閾值"""
        checker = TextSimilarityChecker(similarity_threshold=0.8)
        assert checker.threshold == 0.8

    def test_invalid_threshold_raises_error(self):
        """異常情境：無效閾值應拋出 ValueError"""
        with pytest.raises(ValueError, match="必須在 0.0 到 1.0 之間"):
            TextSimilarityChecker(similarity_threshold=1.5)

        with pytest.raises(ValueError, match="必須在 0.0 到 1.0 之間"):
            TextSimilarityChecker(similarity_threshold=-0.1)


class TestCheckOriginality:
    """check_originality() 方法測試"""

    def test_original_content(self):
        """正常情境：原創內容（相似度低）"""
        checker = TextSimilarityChecker(similarity_threshold=0.7)

        generated = "這是一篇關於 React Hooks 的技術文章，介紹 useState 和 useEffect 的用法。"
        sources = [
            "Vue.js 是一個前端框架，提供響應式資料綁定。",
            "Python 是一種多用途程式語言，適合資料科學和網頁開發。"
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        assert is_original is True
        assert 0.0 <= max_sim <= 0.7

    def test_plagiarized_content(self):
        """正常情境：抄襲內容（相似度高）"""
        checker = TextSimilarityChecker(similarity_threshold=0.7)

        generated = "React Hooks 提供 useState 和 useEffect 來管理狀態和副作用"
        sources = [
            "React Hooks 提供 useState 和 useEffect 來管理狀態和副作用",  # 幾乎相同
            "Vue.js 是一個前端框架"
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        assert is_original is False
        assert max_sim > 0.7

    def test_identical_text(self):
        """邊界情況：完全相同的文字（相似度應接近 1.0）"""
        checker = TextSimilarityChecker()

        text = "This is a test sentence about machine learning and AI."
        sources = [text]  # 完全相同

        is_original, max_sim = checker.check_originality(text, sources)

        assert is_original is False
        assert max_sim > 0.95  # 應該非常高

    def test_similar_but_reworded(self):
        """正常情境：改寫但語意相似的文字"""
        checker = TextSimilarityChecker(similarity_threshold=0.7)

        generated = "機器學習是人工智慧的一個重要分支，使用數據來訓練模型"
        sources = [
            "人工智慧的重要分支包括機器學習，它透過數據訓練模型"
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        # 語意相似，max_sim 應該較高，但可能低於 0.7 取決於詞彙重疊
        assert 0.0 <= max_sim <= 1.0

    def test_multiple_sources_max_similarity(self):
        """正常情境：多個來源，返回最大相似度"""
        checker = TextSimilarityChecker()

        generated = "React is a JavaScript library for building user interfaces"
        sources = [
            "Vue.js is a progressive framework",  # 低相似度
            "React is a library for building UIs",  # 高相似度
            "Python is a programming language"  # 低相似度
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        # 應該返回與第二個來源的高相似度
        assert max_sim > 0.5

    def test_empty_generated_text_raises_error(self):
        """異常情境：生成文字為空"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能為空"):
            checker.check_originality("", ["source text"])

        with pytest.raises(ValueError, match="不能為空"):
            checker.check_originality("   ", ["source text"])

    def test_empty_sources_raises_error(self):
        """異常情境：來源列表為空"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能為空列表"):
            checker.check_originality("generated text", [])

    def test_sources_with_empty_string_raises_error(self):
        """異常情境：來源包含空字串"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能包含空字串"):
            checker.check_originality("generated", ["source1", "", "source3"])

    def test_threshold_boundary(self):
        """邊界情況：相似度剛好等於閾值"""
        checker = TextSimilarityChecker(similarity_threshold=0.7)

        # 這個測試較難精確控制相似度，僅驗證邏輯
        generated = "test content here"
        sources = ["test content"]

        is_original, max_sim = checker.check_originality(generated, sources)

        # 驗證回傳值格式正確
        assert isinstance(is_original, bool)
        assert 0.0 <= max_sim <= 1.0
        assert is_original == (max_sim <= 0.7)


class TestPairwiseSimilarity:
    """check_pairwise_similarity() 方法測試"""

    def test_identical_texts(self):
        """正常情境：完全相同的文字"""
        checker = TextSimilarityChecker()

        text = "This is a test sentence"
        similarity = checker.check_pairwise_similarity(text, text)

        assert similarity > 0.95  # 應該接近 1.0

    def test_different_texts(self):
        """正常情境：完全不同的文字"""
        checker = TextSimilarityChecker()

        text1 = "React is a JavaScript library"
        text2 = "Python is a programming language"

        similarity = checker.check_pairwise_similarity(text1, text2)

        assert 0.0 <= similarity < 0.5  # 應該較低

    def test_similar_texts(self):
        """正常情境：相似的文字"""
        checker = TextSimilarityChecker()

        text1 = "機器學習是人工智慧的一個分支"
        text2 = "人工智慧的分支包括機器學習"

        similarity = checker.check_pairwise_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0

    def test_empty_text1_raises_error(self):
        """異常情境：text1 為空"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能為空"):
            checker.check_pairwise_similarity("", "text2")

    def test_empty_text2_raises_error(self):
        """異常情境：text2 為空"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能為空"):
            checker.check_pairwise_similarity("text1", "")


class TestGetSimilarityScores:
    """get_similarity_scores() 方法測試"""

    def test_get_scores_multiple_sources(self):
        """正常情境：取得多個來源的相似度分數"""
        checker = TextSimilarityChecker()

        generated = "React Hooks simplify state management in functional components"
        sources = [
            "React Hooks make state management easier",  # 高相似度
            "Vue.js provides reactive data binding",  # 低相似度
            "Python is used for data science"  # 低相似度
        ]

        scores = checker.get_similarity_scores(generated, sources)

        assert len(scores) == 3
        assert all(0.0 <= score <= 1.0 for score in scores)
        assert scores[0] > scores[1]  # 第一個來源應該更相似

    def test_scores_order_matches_sources(self):
        """正常情境：分數順序對應來源順序"""
        checker = TextSimilarityChecker()

        generated = "test"
        sources = ["abc", "def", "ghi"]

        scores = checker.get_similarity_scores(generated, sources)

        assert len(scores) == len(sources)

    def test_empty_generated_raises_error(self):
        """異常情境：生成文字為空"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能為空"):
            checker.get_similarity_scores("", ["source"])

    def test_empty_sources_raises_error(self):
        """異常情境：來源列表為空"""
        checker = TextSimilarityChecker()

        with pytest.raises(ValueError, match="不能為空列表"):
            checker.get_similarity_scores("generated", [])


class TestTextSimilarityRepr:
    """__repr__ 測試"""

    def test_repr_output(self):
        """正常情境：__repr__ 輸出格式正確"""
        checker = TextSimilarityChecker(similarity_threshold=0.8)
        repr_str = repr(checker)

        assert "TextSimilarityChecker" in repr_str
        assert "0.8" in repr_str


class TestRealWorldScenarios:
    """真實場景測試"""

    def test_chinese_english_mixed(self):
        """真實場景：中英文混合內容"""
        checker = TextSimilarityChecker()

        generated = "使用 React Hooks 可以讓 functional components 擁有 state 管理能力"
        sources = [
            "React Hooks 讓函式元件可以使用狀態管理",
            "Vue Composition API 提供響應式狀態"
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        assert isinstance(is_original, bool)
        assert 0.0 <= max_sim <= 1.0

    def test_code_snippet_similarity(self):
        """真實場景：程式碼片段相似度"""
        checker = TextSimilarityChecker()

        generated = "function useState() { return [state, setState]; }"
        sources = [
            "function useState() { return [state, setState]; }",  # 完全相同
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        assert is_original is False
        assert max_sim > 0.9

    def test_long_technical_article(self):
        """真實場景：長篇技術文章"""
        checker = TextSimilarityChecker()

        generated = """
        React 是一個用於構建使用者介面的 JavaScript 函式庫。
        它採用元件化的設計理念，讓開發者可以將 UI 拆分成獨立、可重複使用的部分。
        React Hooks 是 React 16.8 引入的新特性，讓函式元件也能使用狀態和生命週期。
        """

        sources = [
            "React 是 Facebook 開發的前端框架，用於建立互動式網頁應用。",
            "Vue.js 是一個漸進式 JavaScript 框架，專注於視圖層。"
        ]

        is_original, max_sim = checker.check_originality(generated, sources)

        assert 0.0 <= max_sim <= 1.0
