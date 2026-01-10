"""
RateLimiter 測試
驗證爬蟲限速功能正確運作
"""
import pytest
import time
import asyncio
from src.services.scraper.rate_limiter import RateLimiter


class TestRateLimiterInitialization:
    """RateLimiter 初始化測試"""

    def test_create_default_limiter(self):
        """正常情境：建立預設 limiter (1 req/s)"""
        limiter = RateLimiter()
        assert limiter.requests_per_second == 1.0
        assert limiter.min_interval == 1.0
        assert limiter.last_request_time is None

    def test_create_custom_limiter(self):
        """正常情境：建立自訂速率 limiter"""
        limiter = RateLimiter(requests_per_second=2.0)
        assert limiter.requests_per_second == 2.0
        assert limiter.min_interval == 0.5

    def test_invalid_rate_raises_error(self):
        """異常情境：requests_per_second <= 0 應拋出 ValueError"""
        with pytest.raises(ValueError, match="必須大於 0"):
            RateLimiter(requests_per_second=0)

        with pytest.raises(ValueError, match="必須大於 0"):
            RateLimiter(requests_per_second=-1)


class TestRateLimiterSyncWait:
    """同步 wait() 方法測試"""

    def test_first_request_no_wait(self):
        """正常情境：第一次請求不需等待"""
        limiter = RateLimiter(requests_per_second=1.0)

        start_time = time.time()
        limiter.wait()
        elapsed = time.time() - start_time

        # 第一次請求應該幾乎不等待
        assert elapsed < 0.1
        assert limiter.last_request_time is not None

    def test_rate_limiting_enforced(self):
        """正常情境：連續請求會被限速"""
        limiter = RateLimiter(requests_per_second=2.0)  # 0.5 秒間隔

        # 第一次請求
        limiter.wait()
        time.sleep(0.2)  # 只等 0.2 秒（不足 0.5 秒）

        # 第二次請求應被限速
        start_time = time.time()
        limiter.wait()
        elapsed = time.time() - start_time

        # 應該額外等待約 0.3 秒（0.5 - 0.2 = 0.3）
        assert 0.25 < elapsed < 0.4

    def test_multiple_requests_timing(self):
        """正常情境：多次請求的時間間隔應符合限速"""
        limiter = RateLimiter(requests_per_second=10.0)  # 0.1 秒間隔

        timestamps = []
        for _ in range(3):
            limiter.wait()
            timestamps.append(time.time())

        # 驗證每次請求間隔約 0.1 秒
        for i in range(len(timestamps) - 1):
            interval = timestamps[i + 1] - timestamps[i]
            assert 0.09 < interval < 0.15

    def test_sufficient_wait_no_blocking(self):
        """正常情境：若已等待足夠時間，不應額外阻塞"""
        limiter = RateLimiter(requests_per_second=1.0)

        limiter.wait()
        time.sleep(1.1)  # 等待超過 min_interval

        # 第二次請求不應阻塞
        start_time = time.time()
        limiter.wait()
        elapsed = time.time() - start_time

        assert elapsed < 0.1


class TestRateLimiterAsyncWait:
    """非同步 await() 方法測試"""

    @pytest.mark.asyncio
    async def test_async_first_request(self):
        """正常情境：非同步第一次請求不需等待"""
        limiter = RateLimiter(requests_per_second=1.0)

        start_time = time.time()
        await limiter.wait_async()
        elapsed = time.time() - start_time

        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_async_rate_limiting(self):
        """正常情境：非同步連續請求會被限速"""
        limiter = RateLimiter(requests_per_second=2.0)  # 0.5 秒間隔

        await limiter.wait_async()
        await asyncio.sleep(0.2)

        start_time = time.time()
        await limiter.wait_async()
        elapsed = time.time() - start_time

        # 應該額外等待約 0.3 秒
        assert 0.25 < elapsed < 0.4

    @pytest.mark.asyncio
    async def test_async_multiple_requests(self):
        """正常情境：非同步多次請求符合限速"""
        limiter = RateLimiter(requests_per_second=5.0)  # 0.2 秒間隔

        timestamps = []
        for _ in range(3):
            await limiter.wait_async()
            timestamps.append(time.time())

        # 驗證間隔
        for i in range(len(timestamps) - 1):
            interval = timestamps[i + 1] - timestamps[i]
            assert 0.18 < interval < 0.25


class TestRateLimiterUtilityMethods:
    """工具方法測試"""

    def test_can_request_now_initial(self):
        """正常情境：初始狀態可立即請求"""
        limiter = RateLimiter()
        assert limiter.can_request_now() is True

    def test_can_request_now_after_request(self):
        """正常情境：請求後立即檢查應返回 False"""
        limiter = RateLimiter(requests_per_second=1.0)
        limiter.wait()

        assert limiter.can_request_now() is False

    def test_can_request_now_after_interval(self):
        """正常情境：等待足夠時間後應可請求"""
        limiter = RateLimiter(requests_per_second=10.0)  # 0.1 秒間隔
        limiter.wait()
        time.sleep(0.15)

        assert limiter.can_request_now() is True

    def test_get_time_until_next_request(self):
        """正常情境：取得剩餘等待時間"""
        limiter = RateLimiter(requests_per_second=2.0)  # 0.5 秒間隔
        limiter.wait()
        time.sleep(0.2)

        remaining = limiter.get_time_until_next_request()
        assert 0.25 < remaining < 0.35

    def test_get_time_until_next_request_ready(self):
        """正常情境：已可請求時返回 0.0"""
        limiter = RateLimiter()
        assert limiter.get_time_until_next_request() == 0.0

        limiter.wait()
        time.sleep(1.1)
        assert limiter.get_time_until_next_request() == 0.0

    def test_reset(self):
        """正常情境：reset() 重置 limiter 狀態"""
        limiter = RateLimiter()
        limiter.wait()
        assert limiter.last_request_time is not None

        limiter.reset()
        assert limiter.last_request_time is None
        assert limiter.can_request_now() is True

    def test_repr(self):
        """正常情境：__repr__ 輸出格式正確"""
        limiter = RateLimiter(requests_per_second=1.5)
        repr_str = repr(limiter)

        assert "RateLimiter" in repr_str
        assert "1.5" in repr_str
        assert "0.667" in repr_str  # min_interval


class TestRateLimiterEdgeCases:
    """邊界情況測試"""

    def test_very_high_rate(self):
        """邊界情況：極高請求速率（100 req/s）"""
        limiter = RateLimiter(requests_per_second=100.0)

        start_time = time.time()
        for _ in range(5):
            limiter.wait()
        elapsed = time.time() - start_time

        # 5 次請求 @ 100 req/s = 0.04 秒
        assert 0.03 < elapsed < 0.06

    def test_very_low_rate(self):
        """邊界情況：極低請求速率（0.5 req/s = 2秒間隔）"""
        limiter = RateLimiter(requests_per_second=0.5)
        assert limiter.min_interval == 2.0

        limiter.wait()
        time.sleep(1.0)  # 等待 1 秒（不足 2 秒）

        start_time = time.time()
        limiter.wait()
        elapsed = time.time() - start_time

        # 應額外等待約 1 秒
        assert 0.9 < elapsed < 1.2

    def test_fractional_rate(self):
        """邊界情況：小數速率（1.5 req/s）"""
        limiter = RateLimiter(requests_per_second=1.5)
        assert abs(limiter.min_interval - 0.6667) < 0.001

    @pytest.mark.asyncio
    async def test_mixed_sync_async_not_recommended(self):
        """異常情境：混用同步與非同步方法（不推薦但應能運作）"""
        limiter = RateLimiter(requests_per_second=2.0)

        limiter.wait()  # 同步
        time.sleep(0.3)
        await limiter.wait_async()  # 非同步

        # 應該仍能正確限速
        assert limiter.last_request_time is not None
