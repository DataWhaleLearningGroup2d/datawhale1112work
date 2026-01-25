# AI伙伴琳奈

这是一个基于AgentScope的AI陪伴伙伴项目，名叫琳奈。

## 功能

1. 交互式聊天：与琳奈进行实时对话。
2. 定时唤起：每15分钟自动唤起琳奈发起会话。
3. 话题采集：每10分钟自动采集有趣话题并保存。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

设置环境变量：

```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

## 运行

```bash
python main.py
```

运行后，可以与琳奈聊天。输入"exit"退出。

后台会自动运行定时任务。