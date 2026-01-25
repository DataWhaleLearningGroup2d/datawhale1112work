import asyncio
from tool import ChatTools

async def test():
    tools = ChatTools()
    topics = await tools.get_topics()
    print(topics)

if __name__ == "__main__":
    asyncio.run(test())