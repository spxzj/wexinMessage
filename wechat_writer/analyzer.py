from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from statistics import mean
import re


@dataclass
class ArticleFeatures:
    title: str
    paragraph_count: int
    avg_paragraph_length: float
    heading_count: int
    emoji_count: int
    question_sentence_count: int
    call_to_action_count: int
    keywords: list[str]


CTA_PATTERNS = [r"关注", r"点赞", r"在看", r"转发", r"收藏", r"评论", r"私信"]


class _SimpleHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._stack: list[str] = []
        self._buf: list[str] = []
        self.title = ""
        self.paragraphs: list[str] = []
        self.heading_count = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        self._stack.append(tag)
        if tag in {"h1", "h2", "h3", "h4"}:
            self.heading_count += 1

    def handle_endtag(self, tag: str) -> None:
        text = "".join(self._buf).strip()
        if tag == "title" and text and not self.title:
            self.title = text
        if tag == "p" and text:
            self.paragraphs.append(text)
        self._buf.clear()
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._stack:
            return
        if self._stack[-1] in {"title", "p", "h1", "h2", "h3", "h4"}:
            self._buf.append(data)


def analyze_article_html(html: str) -> ArticleFeatures:
    parser = _SimpleHTMLExtractor()
    parser.feed(html)

    paragraphs = [p.strip() for p in parser.paragraphs if p.strip()]
    all_text = "\n".join(paragraphs)

    paragraph_count = len(paragraphs)
    avg_paragraph_length = mean([len(p) for p in paragraphs]) if paragraphs else 0.0
    emoji_count = _count_emoji(all_text)
    question_sentence_count = all_text.count("？") + all_text.count("?")
    call_to_action_count = sum(len(re.findall(pat, all_text)) for pat in CTA_PATTERNS)
    keywords = extract_keywords(all_text)

    return ArticleFeatures(
        title=parser.title or "未命名标题",
        paragraph_count=paragraph_count,
        avg_paragraph_length=round(avg_paragraph_length, 2),
        heading_count=parser.heading_count,
        emoji_count=emoji_count,
        question_sentence_count=question_sentence_count,
        call_to_action_count=call_to_action_count,
        keywords=keywords,
    )


def _count_emoji(text: str) -> int:
    return len(re.findall("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", text))


def extract_keywords(text: str, top_n: int = 12) -> list[str]:
    tokens = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    stopwords = {
        "我们", "你们", "他们", "这个", "那个", "什么", "怎么", "已经", "可以",
        "如果", "因为", "所以", "一个", "没有", "不是", "就是", "自己", "进行",
        "以及", "然后", "还是", "还有", "对于", "通过", "需要", "时候", "文章",
    }
    freq: dict[str, int] = {}
    for t in tokens:
        if t in stopwords:
            continue
        freq[t] = freq.get(t, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]]
