"""
Rate Limiter module.
Tracks and enforces Groq free-tier limits:
- 30 requests/minute
- 1,000 requests/day
- 12,000 tokens/minute
- 100,000 tokens/day
"""
import time
import logging
from typing import List, Tuple
from src.config import GROQ_RPM_LIMIT, GROQ_RPD_LIMIT, GROQ_TPM_LIMIT, GROQ_TPD_LIMIT, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

class RateLimitException(Exception):
    """Raised when a rate limit is exceeded."""
    pass

class RateLimiter:
    def __init__(self):
        # Store as lists of (timestamp, count)
        self.request_history: List[Tuple[float, int]] = []
        self.token_history: List[Tuple[float, int]] = []

    def _cleanup(self, now: float):
        """Remove entries older than 1 day"""
        one_day_ago = now - 86400
        self.request_history = [req for req in self.request_history if req[0] > one_day_ago]
        self.token_history = [tok for tok in self.token_history if tok[0] > one_day_ago]

    def _get_usage(self, now: float, history: List[Tuple[float, int]], window_seconds: float) -> int:
        threshold = now - window_seconds
        return sum(count for ts, count in history if ts > threshold)

    def check_limits(self, estimated_tokens: int) -> Tuple[bool, str]:
        """
        Check if we have capacity for 1 request and `estimated_tokens`.
        Returns (is_allowed, reason_if_blocked).
        """
        now = time.time()
        self._cleanup(now)

        # 1. Check Requests Per Minute (RPM)
        rpm_usage = self._get_usage(now, self.request_history, 60)
        if rpm_usage >= GROQ_RPM_LIMIT:
            return False, "Rate limit exceeded: Too many requests per minute. Please wait a moment."

        # 2. Check Tokens Per Minute (TPM)
        tpm_usage = self._get_usage(now, self.token_history, 60)
        if tpm_usage + estimated_tokens > GROQ_TPM_LIMIT:
            return False, "Rate limit exceeded: Too many tokens per minute. Please wait a moment."

        # 3. Check Requests Per Day (RPD)
        rpd_usage = self._get_usage(now, self.request_history, 86400)
        if rpd_usage >= GROQ_RPD_LIMIT:
            return False, "I've reached my daily request limit. Please try again tomorrow."
        elif rpd_usage >= GROQ_RPD_LIMIT * 0.9:
            logger.warning(f"Approaching daily request limit: {rpd_usage}/{GROQ_RPD_LIMIT}")

        # 4. Check Tokens Per Day (TPD)
        tpd_usage = self._get_usage(now, self.token_history, 86400)
        if tpd_usage + estimated_tokens > GROQ_TPD_LIMIT:
            return False, "I've reached my daily token limit. Please try again tomorrow."
        elif tpd_usage + estimated_tokens >= GROQ_TPD_LIMIT * 0.9:
            logger.warning(f"Approaching daily token limit: {tpd_usage}/{GROQ_TPD_LIMIT}")

        return True, ""

    def record_usage(self, tokens: int):
        """Record an actual API call."""
        now = time.time()
        self.request_history.append((now, 1))
        self.token_history.append((now, tokens))
        self._cleanup(now)

# Global instance
rate_limiter = RateLimiter()

def estimate_tokens(text: str) -> int:
    """Rough heuristic: 1 token ~= 4 characters"""
    return (len(text) // 4) + LLM_MAX_TOKENS
