from __future__ import annotations

import argparse
from pathlib import Path
from urllib import request

from .analyzer import analyze_article_html
from .config import AppConfig
from .generator import build_mimic_prompt
from .llm_client import LLMClient


def read_html(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        with request.urlopen(source, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    return Path(source).read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="分析爆款微信公众号文章并模仿生成新文章")
    parser.add_argument("--source", required=True, help="公众号文章 URL 或本地 HTML 文件路径")
    parser.add_argument("--topic", required=True, help="新文章主题")
    parser.add_argument("--config", default="configs/config.example.yaml", help="配置文件路径")
    parser.add_argument("--extra", default="", help="附加写作要求")
    parser.add_argument("--output", default="output.md", help="生成文章输出文件")

    args = parser.parse_args()

    html = read_html(args.source)
    features = analyze_article_html(html)

    config = AppConfig.from_file(args.config)
    prompt = build_mimic_prompt(features, topic=args.topic, extra_requirements=args.extra)

    client = LLMClient(
        base_url=config.base_url,
        model=config.model,
        api_keys=config.api_keys,
        timeout=config.timeout,
    )
    article = client.chat(prompt)

    out = Path(args.output)
    out.write_text(article, encoding="utf-8")

    print("分析完成，生成文章已输出:", out)
    print(f"当前模型提供方: {config.provider}, 模型: {config.model}")
    print("\n=== 分析结果 ===")
    print(features)


if __name__ == "__main__":
    main()
