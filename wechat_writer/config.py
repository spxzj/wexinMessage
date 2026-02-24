from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any
import os


PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "aliyun_bailian": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
    },
}


@dataclass
class AppConfig:
    provider: str
    model: str
    base_url: str
    api_keys: list[str]
    timeout: int = 60

    @classmethod
    def from_file(cls, path: str | Path) -> "AppConfig":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"配置文件不存在: {p}")

        if p.suffix == ".json":
            raw: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
        elif p.suffix in {".yaml", ".yml"}:
            raw = _parse_simple_yaml(p.read_text(encoding="utf-8"))
        else:
            raise ValueError("配置文件必须是 yaml/yml/json")

        provider = str(raw.get("provider", "openai")).strip().lower()
        if provider not in PROVIDER_DEFAULTS:
            raise ValueError(f"不支持的 provider: {provider}，可选: {', '.join(PROVIDER_DEFAULTS)}")

        defaults = PROVIDER_DEFAULTS[provider]
        model = str(raw.get("model", defaults["model"]))
        base_url = str(raw.get("base_url", defaults["base_url"]))
        timeout = int(raw.get("timeout", 60))

        api_keys = _normalize_keys(raw.get("api_keys", []))
        if not api_keys:
            env_key = os.getenv(defaults["env_key"], "").strip()
            if env_key:
                api_keys = [env_key]

        if not api_keys:
            raise ValueError(
                f"未提供 API Key。请在配置文件 api_keys 或环境变量 {defaults['env_key']} 中配置。"
            )

        return cls(provider=provider, model=model, base_url=base_url, api_keys=api_keys, timeout=timeout)


def _normalize_keys(value: Any) -> list[str]:
    if isinstance(value, str):
        parts = [x.strip() for x in value.split(",")]
        return [p for p in parts if p]

    if isinstance(value, list):
        keys = [str(v).strip() for v in value]
        return [k for k in keys if k]

    return []


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """A minimal YAML parser for this project's flat config shape."""
    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("-") and current_list_key:
            item = line[1:].strip().strip('"').strip("'")
            data.setdefault(current_list_key, []).append(item)
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                data[key] = []
                current_list_key = key
            else:
                current_list_key = None
                data[key] = value.strip('"').strip("'")

    return data
