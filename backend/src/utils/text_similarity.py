"""
文字相似度計算模組
使用 Cosine Similarity + TF-IDF 檢測文字抄襲
對應 tasks.md T019, research.md §5
"""
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TextSimilarityChecker:
    """
    文字相似度檢查器
    使用 TF-IDF + Cosine Similarity 判斷生成內容是否過度相似於來源

    閾值：相似度 > 0.7 視為「過度相似」（不符合原創要求）
    """

    def __init__(self, similarity_threshold: float = 0.7):
        """
        初始化相似度檢查器

        Args:
            similarity_threshold: 相似度閾值（預設 0.7）
                                 超過此值視為「過度相似」
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold 必須在 0.0 到 1.0 之間")

        self.threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,  # 最多使用 1000 個特徵詞
            min_df=1,  # 詞必須至少出現 1 次
            stop_words=None  # 保留所有詞（中英文混合，無預設停用詞）
        )

    def check_originality(
        self,
        generated_text: str,
        source_texts: List[str]
    ) -> Tuple[bool, float]:
        """
        檢查生成文字是否為原創內容

        Args:
            generated_text: 生成的文字
            source_texts: 來源文字列表（用於比對）

        Returns:
            (is_original, max_similarity):
                - is_original: True 若原創（相似度 <= threshold），False 若過度相似
                - max_similarity: 與所有來源的最大相似度值 (0.0 ~ 1.0)

        Raises:
            ValueError: 若輸入文字為空或來源列表為空
        """
        # 驗證輸入
        if not generated_text or not generated_text.strip():
            raise ValueError("generated_text 不能為空")
        if not source_texts or len(source_texts) == 0:
            raise ValueError("source_texts 不能為空列表")
        if any(not text or not text.strip() for text in source_texts):
            raise ValueError("source_texts 中不能包含空字串")

        # 合併所有文字進行 TF-IDF 向量化
        all_texts = [generated_text] + source_texts

        try:
            # 計算 TF-IDF 矩陣
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)

            # 計算生成文字（第一個）與所有來源的 Cosine Similarity
            # tfidf_matrix[0:1] = 生成文字的向量
            # tfidf_matrix[1:] = 所有來源文字的向量
            similarities = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:]
            ).flatten()

            # 找出最大相似度
            max_similarity = float(np.max(similarities))

            # 判斷是否原創（相似度不超過閾值）
            is_original = max_similarity <= self.threshold

            return is_original, max_similarity

        except Exception as e:
            # 若 TF-IDF 向量化失敗（例如詞彙不足），預設視為原創
            raise ValueError(f"文字相似度計算失敗: {str(e)}")

    def check_pairwise_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        計算兩段文字的相似度

        Args:
            text1: 第一段文字
            text2: 第二段文字

        Returns:
            相似度值 (0.0 ~ 1.0)
        """
        if not text1 or not text1.strip():
            raise ValueError("text1 不能為空")
        if not text2 or not text2.strip():
            raise ValueError("text2 不能為空")

        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            raise ValueError(f"文字相似度計算失敗: {str(e)}")

    def get_similarity_scores(
        self,
        generated_text: str,
        source_texts: List[str]
    ) -> List[float]:
        """
        取得生成文字與每個來源的相似度分數

        Args:
            generated_text: 生成的文字
            source_texts: 來源文字列表

        Returns:
            相似度分數列表，順序對應 source_texts
        """
        if not generated_text or not generated_text.strip():
            raise ValueError("generated_text 不能為空")
        if not source_texts or len(source_texts) == 0:
            raise ValueError("source_texts 不能為空列表")

        all_texts = [generated_text] + source_texts

        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            similarities = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:]
            ).flatten()
            return similarities.tolist()
        except Exception as e:
            raise ValueError(f"文字相似度計算失敗: {str(e)}")

    def __repr__(self) -> str:
        return f"<TextSimilarityChecker(threshold={self.threshold})>"
