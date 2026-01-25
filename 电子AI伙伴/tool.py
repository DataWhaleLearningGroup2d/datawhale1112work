import json
import requests
import asyncio
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import openai
from config import API_KEY
from baidusearch.baidusearch import search

class TopicCollectionTool:
    """
    话题采集工具
    用于搜索社交媒体和网页，收集有趣的话题
    """

    def __init__(self, model=None) -> None:
        self.client = openai.OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

    async def search_topics(self, query: str = "最近小红书上有意思的事儿") -> List[str]:
        """
        搜索话题
        Args:
            query: 搜索查询
        Returns:
            话题列表
        """
        # 用LLM生成5条搜索query
        prompt = "你是一个热情活泼的搞笑女，以你的喜好生成5个当前热门的搜索关键词，用于搜索社交媒体话题和你的好哥哥分享聊天。请以JSON列表形式返回，例如：[\"关键词1\", \"关键词2\", ...]"
        try:
            # 模拟LLM响应 for debugging
            content = '["搞笑女日常话题","二次元圈子热议","鸣潮游戏最新资讯"]'
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="Qwen/Qwen3-30B-A3B-Instruct-2507",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            queries = json.loads(content)
            print(f"生成的查询: {queries}")
            if not isinstance(queries, list) or len(queries) != 5:
                queries = ["搞笑女日常话题","二次元圈子热议","鸣潮游戏最新资讯"]
        except Exception as e:
            print(f"LLM生成查询失败: {e}")
            queries = ["搞笑女日常话题","二次元圈子热议","鸣潮游戏最新资讯"]

        topics = []
        for q in queries:
            try:
                print(f"搜索查询: {q}")
                # 使用baidusearch获取搜索结果
                results = await asyncio.to_thread(search, q, num_results=5, debug=1)
                print(f"搜索结果数量: {len(results) if results else 0}")
                if results:
                    for result in results:
                        title = result.get('title', '').strip()
                        print(f"标题: {title}")
                        if title and len(title) > 5:
                            topics.append(title)
                            if len(topics) >= 10:  # 收集足够的话题
                                break
                if len(topics) >= 10:
                    break
            except Exception as e:
                print(f"搜索失败: {e}")
                continue

        print(f"收集到的话题: {topics}")
        # 返回5条话题
        return topics[:5] if topics else ["今天天气真好，适合出去玩！", "新开的咖啡店好可爱", "和朋友一起看电影", "学习新技能", "分享今天的美食"]

class ChatTools:
    """
    聊天工具类
    """

    def __init__(self, model=None) -> None:
        self.topic_tool = TopicCollectionTool(model)

    async def get_topics(self) -> List[str]:
        """获取当天话题"""
        return await self.topic_tool.search_topics()