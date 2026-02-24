from __future__ import annotations

from .analyzer import ArticleFeatures


def build_mimic_prompt(features: ArticleFeatures, topic: str, extra_requirements: str | None = None) -> str:
    req = extra_requirements or ""
    keywords = "、".join(features.keywords) if features.keywords else "（无明显关键词）"

    return f"""
请你模仿微信公众号爆款文章风格进行创作，目标主题：{topic}

请遵循这些结构特征：
1. 标题风格参考：{features.title}
2. 正文段落数约：{features.paragraph_count} 段
3. 每段平均字数约：{features.avg_paragraph_length}
4. 小标题数量约：{features.heading_count}
5. 文中可适当加入 emoji（参考数量：{features.emoji_count}）
6. 适当加入提问句（参考数量：{features.question_sentence_count}）
7. 结尾包含互动引导（关注/点赞/在看/转发等，参考次数：{features.call_to_action_count}）
8. 高频关键词可参考：{keywords}

写作要求：
- 语言自然，具备公众号传播感和节奏感。
- 开头 2 段内抓住读者痛点。
- 中间提供 3-5 条可执行建议或案例。
- 结尾要有总结 + 行动号召。
{req}

请直接输出完整文章，不要解释你的思路。
""".strip()
