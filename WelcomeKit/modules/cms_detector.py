#!/usr/bin/env python3
# CMS detection module
# Author: Created for @amkuush

import re
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup

# Configure logger
logger = logging.getLogger(__name__)

# CMS patterns to check
CMS_PATTERNS = {
    "WordPress": [
        r"wp-content",
        r"wp-includes",
        r"WordPress",
        r"woocommerce"
    ],
    "Shopify": [
        r"cdn\.shopify\.com",
        r"shopify\.com",
        r"Shopify\.theme"
    ],
    "Magento": [
        r"Magento",
        r"mage/cookies.js",
        r"var BLANK_URL"
    ],
    "WooCommerce": [
        r"woocommerce",
        r"WooCommerce"
    ],
    "Joomla": [
        r"Joomla!",
        r"joomla",
        r"/components/com_"
    ],
    "Drupal": [
        r"Drupal",
        r"drupal\.org",
        r"drupal\.min\.js"
    ],
    "PrestaShop": [
        r"PrestaShop",
        r"presta_",
        r"var prestashop ="
    ],
    "BigCommerce": [
        r"bigcommerce\.com",
        r"BigCommerce"
    ],
    "OpenCart": [
        r"OpenCart",
        r"catalog/view/"
    ],
    "Wix": [
        r"wix\.com",
        r"Wix\.com",
        r"wixstatic\.com"
    ],
    "Squarespace": [
        r"squarespace\.com",
        r"static1\.squarespace\.com"
    ],
    "TYPO3": [
        r"TYPO3",
        r"typo3"
    ],
    "Ghost": [
        r"ghost\.org",
        r"ghost\.io"
    ],
    "Weebly": [
        r"weebly\.com",
        r"weeblycdn\.com"
    ],
    "Blogger": [
        r"blogger\.com",
        r"blogspot\.com"
    ],
    "Sitecore": [
        r"sitecore",
        r"_sc/"
    ],
    "Sitefinity": [
        r"sitefinity",
        r"Telerik\.Sitefinity"
    ],
    "Adobe Experience Manager": [
        r"wcmmode",
        r"/etc.clientlibs/"
    ],
    "DNN": [
        r"DotNetNuke",
        r"dnncdn\.com"
    ],
    "Kentico": [
        r"kentico",
        r"CMSPages/"
    ],
    "Episerver": [
        r"episerver",
        r"EPiServer"
    ],
    "Umbraco": [
        r"umbraco",
        r"Umbraco"
    ],
    "Liferay": [
        r"liferay",
        r"Liferay\.\w+"
    ],
    "Django": [
        r"django",
        r"csrfmiddlewaretoken"
    ],
    "Laravel": [
        r"laravel",
        r"Laravel"
    ],
    "ASP.NET": [
        r"__VIEWSTATE",
        r"\.aspx"
    ]
}

def detect_cms(html_content: str, soup: BeautifulSoup) -> List[str]:
    """
    Detect CMS used by the website.
    
    Args:
        html_content: The raw HTML content
        soup: BeautifulSoup object of the parsed HTML
        
    Returns:
        List of detected CMS names
    """
    detected_cms = []
    
    try:
        # Check for CMS patterns in the HTML
        for cms, patterns in CMS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE) or \
                   soup.find(string=re.compile(pattern, re.IGNORECASE)):
                    if cms not in detected_cms:
                        detected_cms.append(cms)
                        break  # Once a CMS is detected, no need to check other patterns
    
    except Exception as e:
        logger.error(f"Error detecting CMS: {e}")
    
    return detected_cms