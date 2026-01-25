# -*- coding: utf-8 -*-
"""AI伙伴琳奈主程序."""
import asyncio
import os
import json
import webbrowser
import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from config import API_KEY,TOPIC_COLLECTION_INTERVAL, WAKE_UP_INTERVAL
from agentscope.agent import ReActAgent, UserAgent
from agentscope.tool import Toolkit
from agentscope.formatter import OpenAIChatFormatter
from model import SiliconflowModel
from tool import ChatTools
import os
if not os.path.exists('message'):
    os.makedirs('message')
with open(os.path.join('message', 'messages.json'), 'w') as f:
    json.dump([], f)

if not os.path.exists('topics'):
    os.makedirs('topics')

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

class LinnaeAgent:
    """琳奈AI伙伴Agent."""

    def __init__(self, socketio=None, initial_topics=None):
        self.socketio = socketio
        self.initial_topics = initial_topics or ["今天过得怎么样？", "最近有什么有趣的事吗？", "你喜欢做什么运动？"]
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
        topics = await self.tools.get_topics()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join('topics', f"topics_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=4)
        print(f"采集到话题并保存到 {filename}")

    async def wake_up(self):
        """定时唤起，加载近10分钟的对话历史并生成回复"""
        if os.path.exists(os.path.join('message', 'messages.json')):
            with open(os.path.join('message', 'messages.json'), 'r') as f:
                messages = json.load(f)
            # 过滤最近10分钟的消息
            now = datetime.now()
            recent_messages = [
                m for m in messages
                if datetime.fromisoformat(m['timestamp']) > now - timedelta(minutes=10)
            ]
            if recent_messages:
                # 拼接历史消息作为输入
                history_text = "\n".join([f"{m['sender']}: {m['message']}" for m in recent_messages])
                print(f"加载近10分钟对话历史: {len(recent_messages)} 条消息")
                # 生成回复
                msg = await self.user(f"基于以下对话历史，请作为琳奈回复：\n{history_text}")
                msg = await self.agent(msg)
                bot_message = msg.get_text_content()
                print(f"琳奈回复: {bot_message}")
                if self.socketio:
                    with app.app_context():
                        socketio.emit('message', {'sender': 'bot', 'message': bot_message})

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

        # 保持运行
        await asyncio.sleep(1000000)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global linnae
    print("客户端连接")
    with app.app_context():
        socketio.emit('message', {'sender': 'bot', 'message': '你好！我是琳奈，很高兴见到你！'})
        # 发送话题选项
        topics = linnae.initial_topics
        socketio.emit('message', {
            'sender': 'bot',
            'message': '请选择一个话题开始聊天：',
            'options': topics
        })

@socketio.on('message')
def handle_message(data):
    user_message = data['message']
    print(f"用户: {user_message}")
    # 存储用户消息到本地文件
    with open(os.path.join('message', 'messages.json'), 'r') as f:
        messages = json.load(f)
    messages.append({
        'sender': 'user',
        'message': user_message,
        'timestamp': datetime.now().isoformat()
    })
    with open(os.path.join('message', 'messages.json'), 'w') as f:
        json.dump(messages, f)
    print("消息已存储")
    # 发送用户消息到客户端显示
    with app.app_context():
        socketio.emit('message', {'sender': 'user', 'message': user_message})

linnae = None

async def main():
    global linnae
    # 获取初始话题
    tools = ChatTools()
    initial_topics = await tools.get_topics()
    initial_topics = initial_topics[:3]  # 取前3个
    linnae = LinnaeAgent(socketio, initial_topics)
    socketio.start_background_task(lambda: asyncio.run(linnae.run()))
    # 打开浏览器
    webbrowser.open('http://localhost:5001')
    # 启动Flask服务器
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    asyncio.run(main())