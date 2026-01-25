# Configuration file
import os

# Siliconflow API Key
API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")

# Search API Keys (for tool.py)
GOOGLE_SEARCH_SERPER_API_KEY = os.environ.get("GOOGLE_SEARCH_SERPER_API_KEY", "")
BAIDU_SEARCH_API_KEY = os.environ.get("BAIDU_SEARCH_API_KEY", "")

# Other configurations
TOPIC_COLLECTION_INTERVAL = 1 * 60  # 1 minutes in seconds
WAKE_UP_INTERVAL = 1 * 10  # 10 seconds in seconds