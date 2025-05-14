#!/usr/bin/env python3
# Cloudflare detection module
# Author: Created for @amkuush

import re
import logging
from typing import Dict, Any
from bs4 import BeautifulSoup
import requests

# Configure logger
logger = logging.getLogger(__name__)

# Cloudflare patterns to check
CLOUDFLARE_PATTERNS = [
    r"cloudflare\.com",
    r"cloudflare-static",
    r"__cf_bm=",
    r"cf-ray",
    r"cf-chl-",
    r"cloudflare-app",
    r"Cloudflare",
    r"CloudFlare"
]

def detect_cloudflare(response: requests.Response, html_content: str, soup: BeautifulSoup) -> bool:
    """
    Detect if the website is using Cloudflare.
    
    Args:
        response: The HTTP response object (can be None)
        html_content: The raw HTML content
        soup: BeautifulSoup object of the parsed HTML
        
    Returns:
        True if Cloudflare is detected, False otherwise
    """
    try:
        # Check response headers for Cloudflare if response is not None
        if response is not None and hasattr(response, 'headers'):
            headers = response.headers
            if any(header.lower() == "cf-ray" for header in headers) or \
               any(header.lower().startswith("cf-") for header in headers):
                return True
        
        # Check for Cloudflare patterns in the HTML
        for pattern in CLOUDFLARE_PATTERNS:
            if re.search(pattern, html_content, re.IGNORECASE):
                return True
            
            # Check for patterns in the soup element strings
            for element in soup.find_all(['script', 'meta', 'div']):
                if element.string and re.search(pattern, str(element.string), re.IGNORECASE):
                    return True
    
    except Exception as e:
        logger.error(f"Error detecting Cloudflare: {e}")
    
    return False