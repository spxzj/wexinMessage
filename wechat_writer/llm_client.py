from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from urllib import request, error


@dataclass
class LLMClient:
    base_url: str
    model: str
    api_keys: list[str]
    timeout: int = 60

    def __post_init__(self) -> None:
        if not self.api_keys:
            raise ValueError("至少要提供一个 API Key")
        self._key_cycle = itertools.cycle(self.api_keys)

    def chat(self, prompt: str, temperature: float = 0.8) -> str:
        last_error: Exception | None = None
        for _ in range(len(self.api_keys)):
            api_key = next(self._key_cycle)
            try:
                return self._chat_once(prompt, api_key, temperature)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue

        raise RuntimeError(f"所有 API Key 都请求失败: {last_error}")

    def _chat_once(self, prompt: str, api_key: str, temperature: float) -> str:
        url = self.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": "你是一个擅长模仿微信公众号爆款文风的中文写作助手。"},
                {"role": "user", "content": prompt},
            ],
        }
        req = request.Request(
            url=url,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload).encode("utf-8"),
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTPError {exc.code}: {detail}") from exc

        data = json.loads(body)
        return data["choices"][0]["message"]["content"].strip()
