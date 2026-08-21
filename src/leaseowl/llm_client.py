"""Provider-agnostic LLM client with record/replay.

Two design goals, both learned this project:

1. Provider-agnostic. The evaluation must not be welded to one vendor.
   `LLMClient` is the interface; `GeminiClient` is the first backend.
   An OpenAI or Anthropic backend implements the same `complete()`.

2. Record/replay. Every live call is cached to disk keyed on a hash of
   (model, prompt). A second run with the same inputs returns the cached
   response with no API call, so CI, reviewers, and future runs reproduce
   the exact evaluation with no key and no cost. The API is paid once.

Keys come from the environment (loaded from .env), never from code and
never from a notebook.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Protocol

CACHE_DIR = Path("eval/replays")


def _key(model: str, prompt: str) -> str:
    h = hashlib.sha256(f"{model}\x00{prompt}".encode()).hexdigest()[:16]
    return h


class LLMClient(Protocol):
    model: str

    def complete(self, prompt: str) -> str:
        ...


class ReplayClient:
    """Wraps any client with a disk cache. Replay-only mode (no wrapped
    client) serves the eval offline: a cache miss raises, so a reviewer
    running without a key gets a clear message rather than a silent gap."""

    def __init__(self, inner: LLMClient | None, cache_dir: Path = CACHE_DIR,
                 model: str | None = None) -> None:
        self.inner = inner
        # Cache keys include the model name, so live and replay MUST agree on
        # it. An explicit model wins; otherwise take the live client's model;
        # only fall back to "replay" when neither is given (tests).
        self.model = model or (inner.model if inner else "replay")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def complete(self, prompt: str) -> str:
        path = self.cache_dir / f"{_key(self.model, prompt)}.json"
        if path.exists():
            try:
                cached = json.loads(path.read_text(encoding="utf-8"))["response"]
                self.hits += 1
                return cached
            except (json.JSONDecodeError, KeyError, OSError):
                # Corrupt or partial cache entry (e.g. an interrupted write):
                # treat as a miss and overwrite, rather than crashing.
                path.unlink(missing_ok=True)
        if self.inner is None:
            raise RuntimeError(
                f"replay cache miss and no live client; missing {path.name}. "
                "Run once with a live client (API key) to populate the cache."
            )
        self.misses += 1
        response = self.inner.complete(prompt)
        # Atomic write: fill a temp file, then replace, so a failure never
        # leaves a half-written cache entry behind.
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(
            {"model": self.model, "prompt": prompt, "response": response},
            ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        return response


class GeminiClient:
    """Google Gemini backend. Reads GOOGLE_API_KEY from the environment.

    Resilient by design: transient server errors (503 high-demand) and
    rate-limit responses (429) are retried with exponential backoff, and
    a minimum interval between calls keeps the free tier (15 req/min)
    happy. Combined with the caller's on-disk cache, a long run survives
    the intermittent failures a free tier inevitably produces."""

    def __init__(self, model: str = "gemini-3.6-flash",
                 min_interval_s: float = 1.0, max_retries: int = 5) -> None:
        from google import genai  # imported lazily so offline replay needs no SDK
        if not os.getenv("GOOGLE_API_KEY"):
            raise RuntimeError("GOOGLE_API_KEY not set (put it in .env)")
        self._genai = genai
        self._client = genai.Client()
        self.model = model
        self.min_interval_s = min_interval_s
        self.max_retries = max_retries
        self._last_call = 0.0

    def complete(self, prompt: str) -> str:
        import time
        from google.genai import errors
        # Pace requests to stay under the free-tier rate limit.
        wait = self.min_interval_s - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                resp = self._client.models.generate_content(
                    model=self.model, contents=prompt)
                self._last_call = time.monotonic()
                return (resp.text or "").strip()
            except (errors.ServerError, errors.ClientError) as e:
                code = getattr(e, "code", None)
                if code in (429, 500, 503) and attempt < self.max_retries - 1:
                    backoff = 2 ** attempt * 3  # 3, 6, 12, 24s
                    print(f"  transient {code}; retrying in {backoff}s "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(backoff)
                    last_exc = e
                    continue
                raise
        raise last_exc
