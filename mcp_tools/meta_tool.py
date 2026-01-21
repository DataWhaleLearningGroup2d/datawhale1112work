# -*- coding: utf-8 -*-
"""Meta tool example."""
import asyncio
import os

from config import GAODE_API_KEY
from agentscope.agent import ReActAgent, UserAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.mcp import HttpStatelessClient
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit


async def main() -> None:
    """Create a stateful MCP client and use it to chat with the model."""

    # 创建高德 MCP client
    client = HttpStatelessClient(
        name="amap",
        transport="streamable_http",
        url=f"https://mcp.amap.com/mcp?key={GAODE_API_KEY}",
    )

    # 创建工具组并注册工具
    toolkit = Toolkit()
    toolkit.create_tool_group(
        "map_tools",
        description="Map related tools",
    )
    await toolkit.register_mcp_client(client, group_name="map_tools")

    # 创建智能体
    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant named Friday.",
        model=DashScopeChatModel(
            model_name="qwen3-max-preview",
            api_key=os.environ["DASHSCOPE_API_KEY"],
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        enable_meta_tool=True,   # 激活元工具和元工具管理
    )

    # 创建用户输入的代理
    user = UserAgent(name="user")

    import json
    print(json.dumps(toolkit.get_json_schemas(), indent=4, ensure_ascii=False))

    # 通过消息的显式传递构建对话逻辑
    msg = None
    while True:
        msg = await agent(msg)
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break


asyncio.run(main())

# Query:
# - 搜索阿里云谷园区附近的咖啡厅
