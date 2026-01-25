# Configuration file
import os

# Siliconflow API Key
API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")

# Other configurations
TOPIC_COLLECTION_INTERVAL = 10 * 60  # 10 minutes in seconds
WAKE_UP_INTERVAL = 15 * 60  # 15 minutes in seconds