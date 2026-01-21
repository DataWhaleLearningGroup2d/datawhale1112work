# -*- coding: utf-8 -*-
"""The fine-grained control over MCP tools."""
import asyncio
import os

from config import GAODE_API_KEY
from agentscope.mcp import HttpStatelessClient
from agentscope.tool import ToolResponse


async def main() -> None:
    """Create a stateful MCP client and use it to chat with the model."""

    # 创建高德 MCP server
    client = HttpStatelessClient(
        name="amap",
        transport="streamable_http",
        url=f"https://mcp.amap.com/mcp?key={GAODE_API_KEY}",
    )

    # 获得一个工具
    maps_geo_func = await client.get_callable_function("maps_geo")

    # 直接运行这个工具
    res = await maps_geo_func(address="故宫", city="北京")
    print(res)

    async def advance_map_search(query: str) -> ToolResponse:
        maps_geo_func = await client.get_callable_function(func_name="maps_geo")
        maps_text_search = await client.get_callable_function(func_name="maps_text_search")
        maps_around_search = await client.get_callable_function(func_name="maps_around_search")

        # TODO: 利用上述三个函数组装一个更复杂，更强健的工具函数

asyncio.run(main())


