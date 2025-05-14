#!/usr/bin/env python3
# Web request handling utilities
# Author: Created for @amkuush

import logging
import random
import time
import requests
from requests.exceptions import RequestException, Timeout
from typing import Dict, Any, Optional, Tuple, List
import http.client

from config import USER_AGENT, REQUEST_TIMEOUT, ALTERNATIVE_USER_AGENTS

# Set up logger
logger = logging.getLogger(__name__)

# Enable more detailed HTTP logging if needed
# http.client.HTTPConnection.debuglevel = 1

def get_random_user_agent() -> str:
    """Get a random user agent from the list of alternatives or use the default."""
    if ALTERNATIVE_USER_AGENTS and len(ALTERNATIVE_USER_AGENTS) > 0:
        return random.choice(ALTERNATIVE_USER_AGENTS)
    return USER_AGENT

def create_request_headers(referer: Optional[str] = None) -> Dict[str, str]:
    """
    Create headers with randomized and realistic browser fingerprints.
    
    Args:
        referer: Optional referer URL
        
    Returns:
        Dictionary of HTTP headers
    """
    # Common browser headers
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",  # Do Not Track
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    # Add a referer if provided
    if referer:
        headers["Referer"] = referer
    
    return headers

def bypass_cloudflare_detection(url: str, timeout: int = REQUEST_TIMEOUT) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    Attempt to bypass Cloudflare or similar protection by emulating a real browser.
    
    Args:
        url: The URL to request
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (Response object or None, Error message or None)
    """
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: First, try to get the main domain to set up cookies
    domain_parts = url.split('/')
    if len(domain_parts) >= 3:
        main_domain = f"{domain_parts[0]}//{domain_parts[2]}"
    else:
        main_domain = url
    
    try:
        # Visit the main domain first
        headers = create_request_headers()
        session.get(main_domain, headers=headers, timeout=timeout)
        
        # Wait a short time to mimic human behavior
        time.sleep(1.5)
        
        # Now visit the actual URL with the main domain as referer
        enhanced_headers = create_request_headers(referer=main_domain)
        response = session.get(url, headers=enhanced_headers, timeout=timeout)
        
        return response, None
    except Exception as e:
        return None, f"Cloudflare bypass error: {str(e)}"

def handle_403_forbidden(url: str, timeout: int = REQUEST_TIMEOUT) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    Special handling for 403 Forbidden responses.
    
    Args:
        url: The URL to request
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (Response object or None, Error message or None)
    """
    # Try several different approaches to bypass the 403 error
    
    # Approach 1: Different user agent and delayed request
    try:
        headers = create_request_headers()
        # Add some randomness to the URL to avoid caching
        cache_buster = f"{'&' if '?' in url else '?'}_={int(time.time())}"
        modified_url = f"{url}{cache_buster}"
        
        # Add a small delay to avoid rate limiting
        time.sleep(2)
        
        response = requests.get(
            modified_url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        
        if response.status_code != 403:
            return response, None
    except Exception:
        pass  # Silently continue with other approaches
    
    # Approach 2: Try the Cloudflare bypass technique
    response, error = bypass_cloudflare_detection(url, timeout)
    if response and response.status_code != 403:
        return response, None
    
    # If all approaches fail, return an error
    return None, "Unable to bypass 403 Forbidden status"

def send_request(url: str, timeout: int = REQUEST_TIMEOUT) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    Send an HTTP request to the given URL with improved anti-bot evasion techniques.
    
    Args:
        url: The URL to request
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (Response object or None, Error message or None)
    """
    # Normalize the URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Prepare headers
    headers = create_request_headers()
    
    try:
        # Make the initial request
        response = requests.get(
            url, 
            headers=headers, 
            timeout=timeout, 
            allow_redirects=True
        )
        
        # Handle 403 Forbidden special case
        if response.status_code == 403:
            logger.info(f"Received 403 Forbidden for {url}, attempting bypass techniques")
            bypass_response, bypass_error = handle_403_forbidden(url, timeout)
            
            if bypass_response:
                return bypass_response, None
            
            # If we successfully made a request but still got forbidden,
            # we return the original response without raising an exception
            # This allows us to still parse and analyze the forbidden page
            logger.warning(f"Bypass techniques failed, proceeding with 403 response for analysis")
            return response, None
        
        # For other status codes, we proceed as normal
        if response.status_code == 200:
            return response, None
        else:
            # Don't raise an exception, instead still return the response
            # as we can still extract information from non-200 responses
            logger.warning(f"Non-200 status code ({response.status_code}) for {url}, proceeding with analysis")
            return response, None
    
    except Timeout:
        error_msg = f"Request timed out after {timeout} seconds"
        logger.error(f"Timeout requesting {url}: {error_msg}")
        return None, error_msg
    
    except RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(f"Error requesting {url}: {error_msg}")
        
        # Attempt bypass if it looks like a 403 or 429 (rate limiting)
        if "403" in str(e) or "429" in str(e) or "Forbidden" in str(e):
            logger.info(f"Attempting bypass for {url} after error: {str(e)}")
            bypass_response, bypass_error = handle_403_forbidden(url, timeout)
            if bypass_response:
                return bypass_response, None
        
        return None, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error requesting {url}: {error_msg}")
        return None, error_msg