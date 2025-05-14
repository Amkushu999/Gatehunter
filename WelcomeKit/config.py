#!/usr/bin/env python3
# GateHunter Bot Configuration
# Author: Created for @amkuush

import os
import logging
from typing import List

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - use environment variable with fallback
BOT_TOKEN = os.getenv("BOT_TOKEN", "8027759653:AAGo1X4dNs-0B2LzykRGeh1s3jfk89jPR9g")

# Admin IDs - list of Telegram user IDs who have admin privileges
ADMIN_IDS = [6125015131, 7325746010]

# Log group ID - group where scan results will be automatically posted
LOG_GROUP_ID = -4663321496

# Report channel ID - where scan results will be sent
REPORT_CHANNEL_ID = -4663321496

# Maximum scan time (in seconds) - set to a very high value to effectively disable timeout
MAX_SCAN_TIME = 600  # 10 minutes

# Maximum concurrent scans per user
MAX_CONCURRENT_SCANS = 1

# Database file path (SQLite)
DB_FILE = "gatehunter.db"

# Status emojis for processing animation
STATUS_EMOJIS = ["🟡", "🟠", "🔵", "🟣", "🟢", "🔴"]

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Alternative user agents to rotate and avoid detection
ALTERNATIVE_USER_AGENTS: List[str] = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # Mobile User Agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
]

# Request timeout (in seconds)
REQUEST_TIMEOUT = 10

# Check if the log group ID is valid
def validate_config():
    """Validate the configuration settings."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Bot token not set. Please set the BOT_TOKEN environment variable.")
        return False
    
    if not ADMIN_IDS:
        logger.warning("No admin IDs specified. Admin features will not be available.")
    
    if not LOG_GROUP_ID:
        logger.warning("Log group ID not set. Results will not be logged to a group.")
    
    return True