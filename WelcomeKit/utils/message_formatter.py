#!/usr/bin/env python3
# Message formatting utilities for the Telegram bot
# Author: Created for @amkuush

import html
import time
from typing import Dict, Any, Optional
from telegram import User

from utils.quotes import get_random_quote

def format_processing_message(url: str, status_emoji: str, user: Optional[User] = None, quote: Optional[str] = None) -> str:
    """
    Format the processing message with status emoji and quote.
    
    Args:
        url: The URL being processed
        status_emoji: Emoji to indicate current status
        user: The user who initiated the scan (optional)
        quote: The quote to display (if None, a random one will be generated)
    
    Returns:
        Formatted HTML message
    """
    # Format URL for display (with HTML escape)
    safe_url = html.escape(url)
    
    # Get quote (either use provided one or generate a new one)
    if quote is None:
        quote = get_random_quote()
    
    # Create user mention if user is provided
    user_mention = ""
    if user:
        user_mention = f"@{html.escape(user.username)}" if user.username else f"User {user.id}"
    
    # Create processing message with the new format, all in bold
    message = (
        f"<b>#GateHunter| \n[$gate]</b>\n"
        f"<b>━━═━━═━━═━━═━━</b>\n"
        f"<b>[ﾒ] Site🔎-</b> {safe_url}\n"
        f"<b>[ﾒ] Status-</b> Requesting🤖......{status_emoji}\n"
        f"<b>[ﾒ] Req-</b> {user_mention}\n"
        f"<b>[ﾒ]</b> <i>\"{quote}\"</i>\n"
        f"<b>[ﾒ] Dev by</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
    )
    
    return message

def format_final_message(url: str, results: Dict[str, Any], user: Optional[User] = None) -> str:
    """
    Format the final results message.
    
    Args:
        url: The URL that was scanned
        results: Scan results dictionary
        user: The user who initiated the scan (optional)
    
    Returns:
        Formatted HTML message
    """
    # Format URL for display (with HTML escape)
    safe_url = html.escape(url)
    
    # Get actual scan time from results or use default
    scan_time = results.get("scan_time", "2.34")
    
    # Get number of pages checked
    pages_checked = results.get("pages_checked", 1)
    
    # Create user mention if user is provided
    user_mention = ""
    if user:
        user_mention = f"@{html.escape(user.username)}" if user.username else f"User {user.id}"
    
    # Format status code (all in bold)
    status_code = results.get("status", "Unknown")
    status_text = f"<b>{status_code} ✅️</b>" if status_code and status_code == 200 else f"<b>{status_code} ❌</b>"
    
    # Format CMS detection results (all in bold)
    cms_list = results.get("cms", [])
    cms_items = [f"<b>{cms}</b>" for cms in cms_list] if cms_list else []
    cms_text = "<b>Not Detected ❌</b>" if not cms_list else ", ".join(cms_items)
    
    # Format payment gateway detection results (all in bold)
    gateway_list = results.get("payment_gateways", [])
    gateway_items = [f"<b>{gateway}</b>" for gateway in gateway_list] if gateway_list else []
    gateway_text = "<b>Not Detected ❌</b>" if not gateway_list else ", ".join(gateway_items)
    
    # Format CAPTCHA detection results (all in bold)
    captcha_list = results.get("captcha", [])
    captcha_status = "<b>Enabled ✅</b>" if captcha_list else "<b>Disabled ❌</b>"
    
    # Format Cloudflare detection results (all in bold)
    cloudflare = "<b>Detected ✅</b>" if results.get("cloudflare") else "<b>Not Detected ❌</b>"
    
    # We'll keep track of pages checked but not display it
    # depth_info = f"<b>[ϟ] Depth:</b> <b>{pages_checked}</b> pages scanned\n"
    depth_info = ""
    
    # Error handling with special case for 403 Forbidden
    error = results.get("error")
    
    # Create the main section based on conditions
    if error and ("403" in error or "Forbidden" in error):
        # It's a 403 Forbidden error
        error_section = f"<b>[ϟ] Error:</b> {html.escape(error)}\n"
        
        # Show partial results if available even with 403
        if gateway_list or cms_list or captcha_list or results.get("cloudflare"):
            main_section = (
                f"<b>[ϟ] Status:</b> <b>BLOCKED 🔒</b>\n"
                f"<b>[ϟ] Gateaways:</b> {gateway_text}\n"
                f"<b>[ϟ] CMS:</b> {cms_text}\n"
                f"<b>[ϟ] Captcha:</b> {captcha_status}\n"
                f"<b>[ϟ] Cloudflare:</b> {cloudflare}\n"
                f"{depth_info}"
                f"<b>[ϟ] T/t:</b> <b>{scan_time}(s)</b> | [<b>Anti-Bot Bypasser 🛡️</b>]\n"
            )
        else:
            main_section = ""
    elif error:
        # Other types of errors
        error_section = f"<b>[ϟ] Error:</b> {html.escape(error)}\n"
        main_section = ""
    else:
        # No errors
        error_section = ""
        
        # Check if the status code is 403 or other 4xx (blocked)
        if status_code == 403 or str(status_code).startswith('4'):
            main_section = (
                f"<b>[ϟ] Status:</b> <b>BLOCKED 🔒</b>\n"
                f"<b>[ϟ] Gateaways:</b> {gateway_text}\n"
                f"<b>[ϟ] CMS:</b> {cms_text}\n"
                f"<b>[ϟ] Captcha:</b> {captcha_status}\n"
                f"<b>[ϟ] Cloudflare:</b> {cloudflare}\n"
                f"{depth_info}"
                f"<b>[ϟ] T/t:</b> <b>{scan_time}(s)</b> | [<b>Anti-Bot Bypasser 🛡️</b>]\n"
            )
        else:
            # Normal successful scan
            main_section = (
                f"<b>[ϟ] Status:</b> {status_text}\n"
                f"<b>[ϟ] Gateaways:</b> {gateway_text}\n"
                f"<b>[ϟ] CMS:</b> {cms_text}\n"
                f"<b>[ϟ] Captcha:</b> {captcha_status}\n"
                f"<b>[ϟ] Cloudflare:</b> {cloudflare}\n"
                f"{depth_info}"
                f"<b>[ϟ] T/t:</b> <b>{scan_time}(s)</b> | [<b>Px: Live! ✅</b>]\n"
            )
    
    # Create final message with new format, all in bold
    message = (
        f"<b>#GateHunter $gate</b>\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>[ϟ] SITE:</b> {safe_url}\n"
        f"{error_section}{main_section}"
        f"<b>[ϟ] Req:</b> {user_mention}\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
    )
    
    return message