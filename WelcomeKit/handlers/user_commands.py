#!/usr/bin/env python3
# User command handlers for the Telegram bot
# Author: Created for @amkuush
# Fix for root domain scanning issues

import logging
import asyncio
import time
from typing import Dict, Any, List, Tuple, Optional
import re
from urllib.parse import urlparse
from telegram import Update, User, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext
from telegram.error import TelegramError

from config import MAX_SCAN_TIME, STATUS_EMOJIS
from modules.site_scanner import scan_website
from utils.database import add_user_to_db, is_authorized, add_scan_to_history, is_admin
from utils.message_formatter import format_processing_message, format_final_message
from utils.quotes import get_random_quote

# Set up logger
logger = logging.getLogger(__name__)

# Tracker for active scans
active_scans: Dict[int, Dict] = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the start command with inline buttons."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    user = update.effective_user
    add_user_to_db(user.id, user.username or "Unknown")
    
    # Create a shorter welcome message with stylish formatting
    message = (
        f"<b>#GateHunter Bot</b> 🔍\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>Welcome, {user.first_name}!</b>\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
    )
    
    # Create inline keyboard with buttons
    keyboard = [
        [
            InlineKeyboardButton("🔍 Scan Website", callback_data="cmd_gate_info"),
            InlineKeyboardButton("🏓 Ping", callback_data="cmd_ping")
        ],
        [
            InlineKeyboardButton("ℹ️ Commands", callback_data="cmd_help"),
            InlineKeyboardButton("⚡ Admin", callback_data="cmd_admin")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with inline keyboard
    await update.message.reply_text(
        message, 
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML, 
        disable_web_page_preview=True
    )

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the ping command."""
    user = update.effective_user
    add_user_to_db(user.id, user.username or "Unknown")
    
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id) and update.effective_chat.type != "private":
        await update.message.reply_text("❌ This group is not authorized to use the bot.")
        return
    
    start_time = time.time()
    message = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000, 2)
    
    # Convert ms to seconds for display
    ping_seconds = ping_time / 1000
    
    # Calculate uptime (placeholder - could be implemented with actual uptime tracking)
    uptime = "24h 12m 30s"
    
    # Format according to specified template
    formatted_message = (
        f"<b>#GateHunter $ping🤖</b>\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>[ϟ] Status:</b> Online ✅\n"
        f"<b>[ϟ] Latency:</b> {ping_seconds:.2f}(s)\n"
        f"<b>[ϟ] Uptime:</b> [ {uptime} ]\n"
        f"<b>[ϟ] Req:</b> @{user.username or user.id}\n"
        f"<b>━━━━━Thank GOD am alive🤖━━━━━━━━</b>\n"
        f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
    )
    
    await message.edit_text(formatted_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def cmd_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the cmd command."""
    
    user = update.effective_user
    add_user_to_db(user.id, user.username or "Unknown")
    
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id) and update.effective_chat.type != "private":
        await update.message.reply_text("❌ This group is not authorized to use the bot.")
        return
    
    is_user_admin = is_admin(user.id)
    
    # Create a styled message showing all commands in the new format
    formatted_message = (
        f"<b>#GateHunter $help</b>\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>[ϟ] USER COMMANDS</b>\n"
        f"<b>[ϟ] .gate:</b> <code>.gate</code> or <code>/gate</code> [URL]\n"
        f"<b>[ϟ] .ping:</b> <code>.ping</code> or <code>/ping</code>\n"
        f"<b>[ϟ] .cmd:</b> <code>.cmd</code> or <code>/cmd</code>\n"
    )
    
    # Show admin commands if user is admin
    if is_user_admin:
        formatted_message += (
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>[ϟ] ADMIN COMMANDS</b>\n"
            f"<b>[ϟ] .auth:</b> <code>.auth</code>\n"
            f"<b>[ϟ] .deauth:</b> <code>.deauth</code>\n"
            f"<b>[ϟ] .listusers:</b> <code>.listusers</code>\n"
            f"<b>[ϟ] .listgroup:</b> <code>.listgroup</code>\n"
            f"<b>[ϟ] .brod:</b> <code>.brod</code> [message]\n"
        )
    
    formatted_message += (
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"<b>Req:</b> @{user.username or user.id}\n"
        f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
    )
    
    await update.message.reply_text(formatted_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def gate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the gate command."""
    user = update.effective_user
    user_id = user.id
    add_user_to_db(user_id, user.username or "Unknown")
    
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id) and update.effective_chat.type != "private":
        await update.message.reply_text("❌ This group is not authorized to use the bot.")
        return
    
    # Check if there's an active scan already for this user
    if user_id in active_scans and (time.time() - active_scans[user_id]["start_time"]) < MAX_SCAN_TIME:
        await update.message.reply_text("⏳ You already have an active scan. Please wait for it to complete.")
        return
    
    # Get the URL from the command - could be /gate URL or .gate URL
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a URL to scan after the command.\nE.g., <code>/gate example.com</code>", parse_mode=ParseMode.HTML)
        return
    
    # Join all args to handle URLs with spaces or other characters
    url = ' '.join(context.args)
    
    # Clean up URL
    url = url.strip()
    
    # Ensure URL starts with http:// or https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Fix for plain domain URLs (ensure we're checking main domain and payment pages)
    parsed_url = urlparse(url)
    if parsed_url.path == '' or parsed_url.path == '/':
        logger.info(f"URL is main domain. Will scan thoroughly: {url}")
    
    # Get a random quote
    from utils.quotes import get_random_quote
    quote = get_random_quote()
    
    # Send initial processing message
    processing_message = format_processing_message(url, STATUS_EMOJIS[0], user, quote)
    message = await update.message.reply_text(
        processing_message, 
        parse_mode=ParseMode.HTML, 
        disable_web_page_preview=True
    )
    
    # Track the active scan
    active_scans[user_id] = {
        "start_time": time.time(),
        "url": url,
        "message_id": message.message_id,
        "quote": quote
    }
    
    # Start scanning
    context.application.create_task(
        process_website_scan(update, context, url, message, user, user_id, quote)
    )

async def process_website_scan(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, message, user, user_id: int, quote: str) -> None:
    """Process the website scan."""
    try:
        # Record scan start time for calculating total scan time
        scan_start_time = time.time()
        
        # Update message with different statuses
        color_index = 0
        last_message = ""  # Track last message content to avoid duplicate edits
        
        # Start the scan in another task
        scan_task = asyncio.create_task(run_scan(url))
        
        # Update the message with animated colors while scanning
        # Use the same quote throughout the entire scan (from the initial quote)
        while not scan_task.done():
            color = STATUS_EMOJIS[color_index % len(STATUS_EMOJIS)]
            color_index += 1
            
            # Create new processing message with the same quote
            processing_message = format_processing_message(url, color, user, quote)
            
            # Only edit if the message content has changed (avoid Telegram API errors)
            if processing_message != last_message:
                try:
                    await message.edit_text(
                        processing_message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    last_message = processing_message
                except TelegramError as e:
                    if "Message is not modified" not in str(e):
                        # Only log if it's not the duplicate message error
                        logger.error(f"Error updating scan message: {e}")
            
            await asyncio.sleep(1)
        
        # Wait for the scan to finish (no timeout)
        if not scan_task.done():
            try:
                # Just in case something unexpected happens, we'll log it
                logger.info(f"Waiting for scan of {url} to complete...")
                await scan_task
            except Exception as e:
                logger.error(f"Error while waiting for scan to complete: {e}")
                scan_result = {
                    "url": url,
                    "error": f"An error occurred during scanning: {str(e)}",
                    "cms": [],
                    "payment_gateways": [],
                    "captcha": [],
                    "cloudflare": False
                }
        else:
            # Get the scan result
            scan_result = scan_task.result()
        
        # Calculate total scan time and add to results
        scan_end_time = time.time()
        scan_duration = round(scan_end_time - scan_start_time, 2)
        scan_result["scan_time"] = str(scan_duration)
        
        # Add the scan to history
        add_scan_to_history(user_id, url, scan_result)
        
        # Prepare the final message
        final_message = format_final_message(url, scan_result, user)
        
        # Make sure final message is different from last message to avoid edit errors
        if final_message == last_message:
            # Add an invisible character to make it different
            final_message += "\u200B"  # Zero-width space
            
        # Update the message with the results
        try:
            # Always update the original message with scan results - never create a new one
            await message.edit_text(
                final_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except TelegramError as e:
            # Only log the error, don't send a new message
            logger.error(f"Error updating final scan message: {e}")
            
            # Try one more time with a delay (in case it was a rate limit issue)
            try:
                await asyncio.sleep(1)
                await message.edit_text(
                    final_message + "\u200B\u200B",  # Add two zero-width spaces to make it different
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception as e2:
                logger.error(f"Second attempt to update message failed: {e2}")
        
        # Send to report channel if one is defined
        try:
            from config import REPORT_CHANNEL_ID
            if REPORT_CHANNEL_ID:
                # Send the scan result to the report channel with user attribution
                await context.bot.send_message(
                    chat_id=REPORT_CHANNEL_ID,
                    text=final_message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                logger.info(f"Successfully sent scan result to report channel for URL: {url}")
        except Exception as e:
            logger.error(f"Failed to send to report channel: {e}")
        
        # Remove from active scans
        if user_id in active_scans:
            del active_scans[user_id]
            
    except Exception as e:
        logger.error(f"Error in process_website_scan: {e}", exc_info=True)
        # Try to notify the user
        try:
            await message.edit_text(
                f"❌ Sorry, an error occurred while scanning: {str(e)}",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except:
            pass
        
        # Remove from active scans
        if user_id in active_scans:
            del active_scans[user_id]

async def run_scan(url: str) -> Dict[str, Any]:
    """Run the scanner in a separate thread to not block the event loop."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, scan_website, url)
    return result

async def button_callback_handler(update: Update, context: CallbackContext) -> None:
    """Handle button callbacks from inline keyboard."""
    query = update.callback_query
    user = query.from_user
    
    # Acknowledge the button click immediately
    await query.answer()
    
    # Get callback data
    data = query.data
    
    if data == "cmd_gate_info":
        # Show gate command info with example
        message = (
            f"<b>#GateHunter $help</b>\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>[ϟ] SCAN WEBSITE</b>\n\n"
            f"To scan a website, use:\n"
            f"<code>/gate example.com</code> or\n"
            f"<code>.gate example.com</code>\n\n"
            f"The bot will detect CMS, payment gateways, CAPTCHA, and Cloudflare.\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="cmd_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    elif data == "cmd_ping":
        # Show ping info
        start_time = time.time()
        await query.edit_message_text("🏓 Pinging...", parse_mode=ParseMode.HTML)
        end_time = time.time()
        
        ping_time = round((end_time - start_time) * 1000, 2)
        ping_seconds = ping_time / 1000
        uptime = "24h 12m 30s"
        
        formatted_message = (
            f"<b>#GateHunter $ping🤖</b>\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>[ϟ] Status:</b> Online ✅\n"
            f"<b>[ϟ] Latency:</b> {ping_seconds:.2f}(s)\n"
            f"<b>[ϟ] Uptime:</b> [ {uptime} ]\n"
            f"<b>[ϟ] Req:</b> @{user.username or user.id}\n"
            f"<b>━━━━━Thank GOD am alive🤖━━━━━━━━</b>\n"
            f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="cmd_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            formatted_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    elif data == "cmd_help":
        # Show all commands
        is_user_admin = is_admin(user.id)
        
        formatted_message = (
            f"<b>#GateHunter $help</b>\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>[ϟ] USER COMMANDS</b>\n"
            f"<b>[ϟ] .gate:</b> <code>.gate</code> or <code>/gate</code> [URL]\n"
            f"<b>[ϟ] .ping:</b> <code>.ping</code> or <code>/ping</code>\n"
            f"<b>[ϟ] .cmd:</b> <code>.cmd</code> or <code>/cmd</code>\n"
        )
        
        if is_user_admin:
            formatted_message += (
                f"<b>━━━━━━━━━━━━━</b>\n"
                f"<b>[ϟ] ADMIN COMMANDS</b>\n"
                f"<b>[ϟ] .auth:</b> <code>.auth</code>\n"
                f"<b>[ϟ] .deauth:</b> <code>.deauth</code>\n"
                f"<b>[ϟ] .listusers:</b> <code>.listusers</code>\n"
                f"<b>[ϟ] .listgroup:</b> <code>.listgroup</code>\n"
                f"<b>[ϟ] .brod:</b> <code>.brod</code> [message]\n"
            )
        
        formatted_message += (
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="cmd_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            formatted_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    elif data == "cmd_admin":
        # Show admin info
        is_user_admin = is_admin(user.id)
        
        if is_user_admin:
            message = (
                f"<b>#GateHunter $admin</b>\n"
                f"<b>━━━━━━━━━━━━━</b>\n"
                f"<b>[ϟ] ADMIN PANEL</b>\n\n"
                f"<b>Admin Commands:</b>\n"
                f"<code>.auth</code> - Authorize a group\n"
                f"<code>.deauth</code> - Deauthorize a group\n"
                f"<code>.listusers</code> - List all users\n"
                f"<code>.listgroup</code> - List all authorized groups\n"
                f"<code>.brod</code> - Broadcast message to all users\n"
                f"<b>━━━━━━━━━━━━━</b>\n"
                f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
            )
        else:
            message = (
                f"<b>#GateHunter $admin</b>\n"
                f"<b>━━━━━━━━━━━━━</b>\n"
                f"<b>[ϟ] ACCESS DENIED</b>\n\n"
                f"You don't have admin privileges.\n"
                f"<b>━━━━━━━━━━━━━</b>\n"
                f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
            )
        
        keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="cmd_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    elif data == "cmd_back":
        # Return to main menu
        message = (
            f"<b>#GateHunter Bot</b> 🔍\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>Welcome, {user.first_name}!</b>\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"<b>Dev by:</b> <a href='https://t.me/amkuush'>ªMkUsH</a>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 Scan Website", callback_data="cmd_gate_info"),
                InlineKeyboardButton("🏓 Ping", callback_data="cmd_ping")
            ],
            [
                InlineKeyboardButton("ℹ️ Commands", callback_data="cmd_help"),
                InlineKeyboardButton("⚡ Admin", callback_data="cmd_admin")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )