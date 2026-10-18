"""OpenRouter chat client with an append-only JSONL cache and retries."""

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

API = "https://openrouter.ai/api/v1"
MAX_ATTEMPTS = 5
MIN_INTERVAL = 3.1  # seconds between live calls, under the 20 requests/minute free limit


class LLMError(Exception):
    pass


GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/openai"
GEMINI_PREFIX = "gemini/"
GEMINI_MIN_INTERVAL = 4.1  # free tier allows about 15 requests/minute


def _key(var: str = "OPENROUTER_API_KEY") -> str:
    key = os.environ.get(var)
    if not key:
        raise LLMError(f"{var} is not set")
    return key


def _route(model: str) -> tuple[str, str, str, float]:
    """Return (endpoint, key env var, provider model id, min interval) for a model id."""
    if model.startswith(GEMINI_PREFIX):
        return GEMINI_API, "GEMINI_API_KEY", model[len(GEMINI_PREFIX):], GEMINI_MIN_INTERVAL
    return API, "OPENROUTER_API_KEY", model, MIN_INTERVAL


class LLM:
    def __init__(self, cache_path: Path, transport: httpx.BaseTransport | None = None, cache_only: bool = False):
        self.cache_only = cache_only  # replay saved answers only; a miss is an error, never a request
        self.cache_path = Path(cache_path)
        self.cache: dict[str, str] = {}
        if self.cache_path.exists():
            for line in self.cache_path.read_text().splitlines():
                row = json.loads(line)
                self.cache[row["key"]] = row["response"]
        self.client = httpx.Client(transport=transport, timeout=120)
        self.live_calls = 0
        self._last: dict[str, float] = {}

    def chat(self, model: str, system: str, user: str, temperature: float = 0.0, max_tokens: int = 800) -> str:
        request = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        if key in self.cache:
            return self.cache[key]
        if self.cache_only:
            raise LLMError("not in cache")
        text = self._post(request)
        self.cache[key] = text
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open("a") as f:
            f.write(json.dumps({"key": key, "model": model, "request": request, "response": text, "ts": time.time()}) + "\n")
        return text

    def _post(self, request: dict) -> str:
        endpoint, key_var, provider_model, interval = _route(request["model"])
        body = {**request, "model": provider_model}
        last_error = ""
        for attempt in range(MAX_ATTEMPTS):
            wait = interval - (time.monotonic() - self._last.get(endpoint, 0.0))
            if wait > 0:
                time.sleep(wait)
            self._last[endpoint] = time.monotonic()
            self.live_calls += 1
            try:
                r = self.client.post(
                    f"{endpoint}/chat/completions",
                    headers={"Authorization": f"Bearer {_key(key_var)}", "X-Title": "tor-words study"},
                    json=body,
                )
            except httpx.HTTPError as e:
                last_error = repr(e)
            else:
                if r.status_code == 200:
                    body = r.json()
                    content = (body.get("choices") or [{}])[0].get("message", {}).get("content")
                    if content is not None and "error" not in body:
                        return content
                    last_error = json.dumps(body.get("error", body))[:300]
                else:
                    last_error = f"HTTP {r.status_code}: {r.text[:300]}"
                    if r.status_code in (400, 401, 402, 403, 404):
                        break
                    retry_after = r.headers.get("retry-after")
                    if retry_after and retry_after.isdigit():
                        time.sleep(int(retry_after))
                        continue
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(2 ** (attempt + 1))
        raise LLMError(last_error)


def list_free_models(transport: httpx.BaseTransport | None = None) -> list[str]:
    r = httpx.Client(transport=transport, timeout=60).get(f"{API}/models")
    r.raise_for_status()
    out = []
    for m in r.json()["data"]:
        price = m.get("pricing", {})
        if m["id"].endswith(":free") and all(str(price.get(k, "0")) in ("0", "0.0") for k in ("prompt", "completion")):
            out.append(m["id"])
    return sorted(out)


def key_info(transport: httpx.BaseTransport | None = None) -> dict:
    r = httpx.Client(transport=transport, timeout=60).get(f"{API}/key", headers={"Authorization": f"Bearer {_key()}"})
    r.raise_for_status()
    return r.json()["data"]
