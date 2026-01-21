# -*- coding: utf-8 -*-
"""Stateful MCP client example."""
import asyncio
import os

from config import DASHSCOPE_API_KEY
from agentscope.agent import ReActAgent, UserAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.mcp import StdIOStatefulClient
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit


async def main() -> None:
    """Create a stateful MCP client and use it to chat with the model."""

    # 创建 浏览器 MCP client
    client = StdIOStatefulClient(
        name="playwright-mcp",
        command="npx",
        args=["@playwright/mcp@latest"],
    )

    # 连接 MCP 服务
    await client.connect()

    # 注册工具
    toolkit = Toolkit()
    await toolkit.register_mcp_client(client)

    # 创建智能体
    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant named Friday.",
        model=DashScopeChatModel(
            model_name="qwen3-max-preview",
            api_key=DASHSCOPE_API_KEY,
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
    )

    # 创建用户输入的代理
    user = UserAgent(name="user")

    # 通过消息的显式传递构建对话逻辑
    msg = None
    while True:
        msg = await agent(msg)
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break

    await client.close()


asyncio.run(main())

# Query:
# - 打开 Google
# - 搜索 AgentScope