import json

import httpx
import pytest

from torwords import llm as llm_mod
from torwords.llm import LLM, LLMError


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-secretvalue123")


def ok(text):
    return httpx.Response(200, json={"choices": [{"message": {"content": text}}]})


def counting(responses):
    calls = []

    def handler(request):
        calls.append(request)
        return responses[min(len(calls), len(responses)) - 1]

    return httpx.MockTransport(handler), calls


def test_cache_hit_skips_network(tmp_path):
    transport, calls = counting([ok("hello")])
    c = LLM(tmp_path / "cache.jsonl", transport=transport)
    assert c.chat("m", "sys", "user") == "hello"
    assert c.chat("m", "sys", "user") == "hello"
    assert len(calls) == 1
    assert len((tmp_path / "cache.jsonl").read_text().splitlines()) == 1


def test_cache_survives_new_instance(tmp_path):
    transport, calls = counting([ok("hello")])
    LLM(tmp_path / "cache.jsonl", transport=transport).chat("m", "s", "u")
    assert LLM(tmp_path / "cache.jsonl", transport=transport).chat("m", "s", "u") == "hello"
    assert len(calls) == 1


def test_retries_on_429_then_succeeds(tmp_path):
    transport, calls = counting([httpx.Response(429), httpx.Response(429), ok("done")])
    assert LLM(tmp_path / "c.jsonl", transport=transport).chat("m", "s", "u") == "done"
    assert len(calls) == 3


def test_gives_up_after_5_attempts(tmp_path):
    transport, calls = counting([httpx.Response(503)])
    with pytest.raises(LLMError):
        LLM(tmp_path / "c.jsonl", transport=transport).chat("m", "s", "u")
    assert len(calls) == 5


def test_key_not_in_cache_file(tmp_path):
    transport, _ = counting([ok("x")])
    LLM(tmp_path / "c.jsonl", transport=transport).chat("m", "s", "u")
    assert "secretvalue123" not in (tmp_path / "c.jsonl").read_text()


def test_sends_bearer_key_and_model(tmp_path):
    transport, calls = counting([ok("x")])
    LLM(tmp_path / "c.jsonl", transport=transport).chat("vendor/model:free", "s", "u")
    assert calls[0].headers["authorization"] == "Bearer sk-or-v1-secretvalue123"
    assert json.loads(calls[0].content)["model"] == "vendor/model:free"


def test_gemini_models_route_to_google(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key-456")
    transport, calls = counting([ok("hi")])
    LLM(tmp_path / "c.jsonl", transport=transport).chat("gemini/gemini-flash-lite", "s", "u")
    req = calls[0]
    assert req.url.host == "generativelanguage.googleapis.com"
    assert req.url.path.endswith("/openai/chat/completions")
    assert req.headers["authorization"] == "Bearer gem-key-456"
    assert json.loads(req.content)["model"] == "gemini-flash-lite"


def test_cache_key_keeps_provider_prefix(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key-456")
    transport, calls = counting([ok("a"), ok("b")])
    c = LLM(tmp_path / "c.jsonl", transport=transport)
    c.chat("gemini/x", "s", "u")
    c.chat("x", "s", "u")
    assert len(calls) == 2


def test_cache_only_raises_on_miss_without_network(tmp_path):
    transport, calls = counting([ok("hello")])
    LLM(tmp_path / "c.jsonl", transport=transport).chat("m", "s", "cached")
    c = LLM(tmp_path / "c.jsonl", transport=transport, cache_only=True)
    assert c.chat("m", "s", "cached") == "hello"
    with pytest.raises(LLMError):
        c.chat("m", "s", "missing")
    assert len(calls) == 1
