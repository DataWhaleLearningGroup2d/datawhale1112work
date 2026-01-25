from agentscope.model import OpenAIChatModel
import os

class SiliconflowModel(OpenAIChatModel):
    """Siliconflow model for AgentScope."""

    def __init__(self, config_name: str, model_name: str, api_key: str = None, **kwargs):
        api_key = api_key or os.environ.get("SILICONFLOW_API_KEY")
        super().__init__(
            config_name=config_name,
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1",
            **kwargs
        )