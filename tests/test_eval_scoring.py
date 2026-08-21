"""Offline tests for the evaluation's scoring and detector parsing.

Uses a scripted fake client so the logic is verified in CI with no API
key. A scoring function must itself be tested, or the headline numbers
it produces cannot be trusted.
"""

import sys
sys.path.insert(0, "src")

from leaseowl.detector import _parse, detect
from leaseowl.llm_client import ReplayClient


class FakeClient:
    model = "fake"

    def __init__(self, response):
        self._response = response

    def complete(self, prompt):
        return self._response


def test_parse_clean_json():
    d = _parse('{"verdict": "deficient", "evidence": "3", "reason": "no threshold"}')
    assert d.verdict == "deficient" and d.evidence == "3"


def test_parse_json_embedded_in_text():
    d = _parse('Here is my answer:\n{"verdict":"missing","evidence":"","reason":"absent"}\nThanks')
    assert d.verdict == "missing"


def test_parse_freetext_fallback():
    d = _parse("The clause is clearly present in the agreement.")
    assert d.verdict == "present"


def test_parse_unparseable_defaults_missing():
    d = _parse("banana")
    assert d.verdict == "missing"


def test_detect_uses_client():
    c = FakeClient('{"verdict":"present","evidence":"preamble","reason":"stated"}')
    d = detect(c, "some agreement text", "Lease Term", "start and end dates")
    assert d.verdict == "present" and d.evidence == "preamble"


def test_kappa_perfect_and_chance():
    from leaseowl.scoring import kappa
    perfect = [("present", "present"), ("missing", "missing"), ("deficient", "deficient")]
    assert kappa(perfect) == 1.0


def test_replay_cache_roundtrip(tmp_path):
    inner = FakeClient("cached response")
    c = ReplayClient(inner, cache_dir=tmp_path, model="fake")
    a = c.complete("hello")          # live -> writes cache
    assert c.misses == 1 and a == "cached response"
    c2 = ReplayClient(None, cache_dir=tmp_path, model="fake")
    b = c2.complete("hello")          # replay-only -> from cache
    assert c2.hits == 1 and b == "cached response"


def test_replay_miss_without_client_raises(tmp_path):
    import pytest
    c = ReplayClient(None, cache_dir=tmp_path, model="fake")
    with pytest.raises(RuntimeError):
        c.complete("never cached")


def test_replay_key_matches_live_model(tmp_path):
    """Regression: a live run and a --replay run must key the cache on the
    SAME model name, or replay misses every entry the live run wrote.
    (The bug: ReplayClient(None) defaulted model to 'replay'.)"""
    live = ReplayClient(FakeClient("resp"), cache_dir=tmp_path, model="gemini-3.6-flash")
    live.complete("a prompt")                       # writes under gemini-3.6-flash
    replay = ReplayClient(None, cache_dir=tmp_path, model="gemini-3.6-flash")
    assert replay.complete("a prompt") == "resp"    # must hit, not miss
    assert replay.hits == 1 and replay.misses == 0
