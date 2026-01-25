# -*- coding: utf-8 -*-
"""AI伙伴琳奈主程序."""
import asyncio
import os
import json
import webbrowser
import threading
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from agentscope.agent import ReActAgent, UserAgent
from agentscope.tool import Toolkit
from agentscope.formatter import OpenAIChatFormatter
from model import SiliconflowModel
from tool import ChatTools
from config import API_KEY, TOPIC_COLLECTION_INTERVAL, WAKE_UP_INTERVAL

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

class LinnaeAgent:
    """琳奈AI伙伴Agent."""

    def __init__(self, socketio=None):
        self.socketio = socketio
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
        message = "琳奈：嘿，朋友！好久不见，你今天过得怎么样？"
        print(message)
        if self.socketio:
            self.socketio.emit('message', {'sender': 'bot', 'message': message})

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
    print("客户端连接")
    socketio.emit('message', {'sender': 'bot', 'message': '你好！我是琳奈，很高兴见到你！'})

@socketio.on('message')
def handle_message(data):
    user_message = data['message']
    print(f"用户: {user_message}")
    # 先发送用户消息到客户端显示
    socketio.emit('message', {'sender': 'user', 'message': user_message})
    print("处理用户消息")
    # 发送正在输入信号
    socketio.emit('typing')
    print("发送typing")
    # 处理bot回复
    threading.Thread(target=lambda: asyncio.run(send_bot_response(user_message))).start()
    print("gevent.spawn called")

async def send_bot_response(user_message):
    print("send_bot_response started")
    global linnae
    print(f"linnae is {linnae}")
    print("开始处理bot回复")
    if API_KEY == "test":
        # 模拟回复
        bot_message = f"你好！我是琳奈，很高兴见到你！你说的是：{user_message}。今天天气真好，我们聊聊你的兴趣爱好吧！"
        print(f"琳奈 (模拟): {bot_message}")
        socketio.emit('message', {'sender': 'bot', 'message': bot_message})
        return
    try:
        msg = await linnae.user(user_message)
        msg = await linnae.agent(msg)
        bot_message = msg.get_text_content()
        print(f"琳奈: {bot_message}")
        socketio.emit('message', {'sender': 'bot', 'message': bot_message})
    except Exception as e:
        error_msg = f"抱歉，我遇到了一些问题：{str(e)}"
        print(f"错误: {error_msg}")
        socketio.emit('message', {'sender': 'bot', 'message': error_msg})

linnae = None

async def main():
    global linnae
    linnae = LinnaeAgent(socketio)
    socketio.start_background_task(lambda: asyncio.run(linnae.run()))
    # 打开浏览器
    webbrowser.open('http://localhost:5001')
    # 启动Flask服务器
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    asyncio.run(main())