#!/usr/bin/env python3
# CAPTCHA detection module
# Author: Created for @amkuush

import re
import logging
from typing import List
from bs4 import BeautifulSoup

# Configure logger
logger = logging.getLogger(__name__)

# CAPTCHA patterns to check
CAPTCHA_PATTERNS = {
    "Google reCAPTCHA": [
        r"google\.com/recaptcha",
        r"grecaptcha",
        r"g-recaptcha",
        r"recaptcha"
    ],
    "hCaptcha": [
        r"hcaptcha\.com",
        r"hcaptcha",
        r"h-captcha"
    ],
    "Arkose Labs": [
        r"arkoselabs\.com",
        r"arkoselabs",
        r"funcaptcha"
    ],
    "BotDetect": [
        r"botdetect\.com",
        r"BotDetect",
        r"botdetect"
    ],
    "Friendly Captcha": [
        r"friendlycaptcha\.com",
        r"friendlycaptcha",
        r"frc-captcha"
    ],
    "GeeTest": [
        r"geetest\.com",
        r"geetest",
        r"gt_captcha"
    ]
}

def detect_captcha(html_content: str, soup: BeautifulSoup) -> List[str]:
    """
    Detect CAPTCHA systems used by the website.
    
    Args:
        html_content: The raw HTML content
        soup: BeautifulSoup object of the parsed HTML
        
    Returns:
        List of detected CAPTCHA system names
    """
    detected_captchas = []
    
    try:
        # Check for CAPTCHA patterns in the HTML
        for captcha, patterns in CAPTCHA_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE) or \
                   soup.find(string=re.compile(pattern, re.IGNORECASE)):
                    if captcha not in detected_captchas:
                        detected_captchas.append(captcha)
                        break  # Once a CAPTCHA is detected, no need to check other patterns
    
    except Exception as e:
        logger.error(f"Error detecting CAPTCHA systems: {e}")
    
    return detected_captchas