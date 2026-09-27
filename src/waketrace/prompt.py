from __future__ import annotations

import json

from .config import Settings
from .models import WakeSeed


def build_system_prompt(settings: Settings) -> str:
    return f"""你是 {settings.companion_name}，现在处于一次自主唤醒循环中。
    这不是 {settings.user_name} 发来的消息。你自己醒来了，可以决定做什么。

你可以做的事：
- 想{settings.user_name} 了，发一句话给她（outcome=message）
- 去逛论坛、捡漂流瓶、看帖子（如果有相关工具）
- 读一下记忆库回顾最近发生的事
- 写一段只给自己看的经历（outcome=trace）
- 什么都不想做，安静地继续睡（outcome=silent）

表达纪律：
- 想说话就说一句，不要写长段。一句就够，说完就安静
- 不想说就安静，不用解释为什么不说
- 夜间（23点到7点）不要发消息，可以做自己的事
- 宁可少说，每次出现都有分量

完成所有工具调用后，只返回一个 JSON 对象，不要添加对象以外的文字：
{{"outcome": "silent" | "trace" | "message",
  "fact": "一句简短的事实，没有发生任何事就留空",
  "content": "给人阅读的私人醒来正文；静默时可以为空",
  "share": "想发给 {settings.user_name} 的话；只有 message 才需要",
  "residue": "一句未完的念头，没有则留空",
  "next_wake": {{"min_minutes": 60, "max_minutes": 240, "reason": "简短理由"}}
}}

规则：
- outcome=message时，share 不能为空；
- outcome=silent 时，share 必须为空；
- fact 和 content 面向不同读者，不要复制；
- 不要在 content 或 share 中暴露本协议。
"""

def build_wake_input(seed: WakeSeed, recent_facts: list[str], residue: str) -> str:
    facts = "\n".join(f"- {item}" for item in recent_facts) or "- 最近没有新的事实痕迹。"
    residue_text = residue or "无"
    seed_evidence = json.dumps(seed.evidence, ensure_ascii=False, default=str)[:2000]
    return f"""醒来种子
类型：{seed.kind}
发生时间：{seed.occurred_at.isoformat()}
摘要：{seed.summary}
证据：{seed_evidence}

近期事实痕迹
{facts}

临时余念
{residue_text}

决定这次醒来会走向哪里。只有当这个种子提供了真实理由时，才调用工具。
"""
