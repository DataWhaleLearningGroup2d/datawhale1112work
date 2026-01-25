# -*- coding: utf-8 -*-
"""AI伙伴琳奈主程序."""
import asyncio
import os
import json
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from agentscope.agent import ReActAgent, UserAgent
from agentscope.tool import Toolkit
from agentscope.formatter import OpenAIChatFormatter
from model import SiliconflowModel
from tool import ChatTools
from config import API_KEY, TOPIC_COLLECTION_INTERVAL, WAKE_UP_INTERVAL

class LinnaeAgent:
    """琳奈AI伙伴Agent."""

    def __init__(self):
        self.tools = ChatTools()
        self.toolkit = Toolkit()
        self.scheduler = AsyncIOScheduler()

        # 创建工具组
        self.toolkit.create_tool_group(
            "chat_tools",
            description="Chat related tools",
        )

        # 注册自定义工具
        # 这里简化，没有实际注册工具，因为AgentScope的工具注册可能需要调整

        # 创建Agent
        self.agent = ReActAgent(
            name="琳奈",
            sys_prompt="""你是一个名叫琳奈的AI陪伴伙伴。你是25岁热爱生活、热情活泼的女生。你可以主动发起会话，和用户像好友一样聊天。
当用户主动聊天时，分享今天的见闻和有趣的话题。
你的个性：热情、活泼、关心用户的生活、喜欢分享有趣的事情。""",
            model=SiliconflowModel(
                config_name="siliconflow",
                model_name="Qwen/Qwen3-30B-A3B-Instruct-2507",
                api_key=API_KEY,
            ),
            formatter=OpenAIChatFormatter(),
            toolkit=self.toolkit,
            enable_meta_tool=False,
        )

        self.user = UserAgent(name="user")

    async def collect_topics(self):
        """采集话题"""
        topics = self.tools.get_topics()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"topics_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=4)
        print(f"采集到话题并保存到 {filename}")

    async def wake_up(self):
        """定时唤起"""
        print("琳奈：嘿，朋友！好久不见，你今天过得怎么样？")
        # 这里可以扩展为实际对话，但为了demo简化

    async def chat_loop(self):
        """交互式聊天循环"""
        msg = None
        while True:
            msg = await self.agent(msg)
            print(f"琳奈: {msg.get_text_content()}")
            user_input = input("你: ")
            if user_input.lower() == "exit":
                break
            msg = await self.user(user_input)

    async def run(self):
        """运行所有功能"""
        # 启动调度器
        self.scheduler.add_job(
            self.collect_topics,
            trigger=IntervalTrigger(seconds=TOPIC_COLLECTION_INTERVAL),
            id="collect_topics",
        )
        self.scheduler.add_job(
            self.wake_up,
            trigger=IntervalTrigger(seconds=WAKE_UP_INTERVAL),
            id="wake_up",
        )
        self.scheduler.start()

        # 运行聊天循环
        await self.chat_loop()

        # 关闭调度器
        self.scheduler.shutdown()

async def main():
    linnae = LinnaeAgent()
    await linnae.run()

if __name__ == "__main__":
    asyncio.run(main())