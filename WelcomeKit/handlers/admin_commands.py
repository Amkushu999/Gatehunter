#!/usr/bin/env python3
# Admin command handlers for the Telegram bot
# Author: Created for @amkuush

import logging
import asyncio
import html
from typing import List, Tuple
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from utils.database import (
    is_admin, 
    authorize_group, 
    deauthorize_group, 
    get_all_users, 
    get_all_groups
)

# Set up logger
logger = logging.getLogger(__name__)

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Authorize a group to use the bot (admin only)."""
    user = update.effective_user
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Check if it's a group
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ This command can only be used in groups.")
        return
    
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or f"Group {chat_id}"
    
    # Authorize the group
    authorize_group(chat_id, chat_title, user.id)
    
    await update.message.reply_text(f"✅ Group {chat_title} has been authorized.")

async def deauth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deauthorize a group (admin only)."""
    user = update.effective_user
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Check if it's a group
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ This command can only be used in groups.")
        return
    
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or f"Group {chat_id}"
    
    # Deauthorize the group
    deauthorize_group(chat_id)
    
    await update.message.reply_text(f"✅ Group {chat_title} has been deauthorized.")

async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all users (admin only)."""
    user = update.effective_user
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("No users found.")
        return
    
    message = "<b>#GateHunter | [User List]</b>\n\n"
    for i, (user_id, username) in enumerate(users, 1):
        message += f"{i}. {html.escape(username)} (ID: {user_id})\n"
    
    message += f"\nTotal Users: {len(users)}"
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def list_groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all authorized groups (admin only)."""
    user = update.effective_user
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    groups = get_all_groups()
    
    if not groups:
        await update.message.reply_text("No authorized groups found.")
        return
    
    message = "<b>#GateHunter | [Group List]</b>\n\n"
    for i, (group_id, group_name) in enumerate(groups, 1):
        message += f"{i}. {html.escape(group_name)} (ID: {group_id})\n"
    
    message += f"\nTotal Groups: {len(groups)}"
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Broadcast a message to all users (admin only).
    Can be used in two ways:
    1. /brod [message text] - sends a text broadcast
    2. Reply to a message (text/photo/video/audio/document) with /brod [optional text] - sends the replied media with optional text
    """
    user = update.effective_user
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Get users
    users = get_all_users()
    if not users:
        await update.message.reply_text("No users found to broadcast to.")
        return
    
    # Check if it's a reply to another message
    broadcast_message = ""
    is_media_broadcast = False
    reply_to_message = update.message.reply_to_message
    
    if context.args:
        broadcast_message = " ".join(context.args)
    
    # Start reply message
    reply = await update.message.reply_text(f"🔄 Broadcasting to {len(users)} users...")
    
    # Determine if it's a media broadcast
    if reply_to_message:
        is_media_broadcast = True
        # Start broadcasting the media with optional text
        await send_media_broadcast(context.bot, broadcast_message, users, reply, reply_to_message)
    else:
        # No message text provided
        if not broadcast_message:
            await reply.edit_text("❌ You need to provide a message. Example: /brod Hello everyone!")
            return
        
        # Start broadcasting text message
        await send_text_broadcast(context.bot, broadcast_message, users, reply)

async def send_text_broadcast(bot, message: str, users: List[Tuple[int, str]], reply_message) -> None:
    """Send text broadcast message to all users."""
    success_count = 0
    failed_count = 0
    
    formatted_message = (
        f"<b>#GateHunter | [BROADCAST]</b>\n\n"
        f"{message}\n\n"
        f"<b>━━━━━━━━━━━━━</b>\n"
        f"Bot by <a href='https://t.me/amkuush'>ªMkUsH</a>"
    )
    
    for user_id, _ in users:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=formatted_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            success_count += 1
        except TelegramError as e:
            logger.error(f"Failed to send broadcast to user {user_id}: {e}")
            failed_count += 1
        
        # Add a small delay to avoid hitting rate limits
        await asyncio.sleep(0.1)
    
    # Update the original message with results
    await reply_message.edit_text(
        f"✅ Broadcast completed!\n"
        f"• Sent to: {success_count} users\n"
        f"• Failed: {failed_count} users"
    )

async def send_media_broadcast(bot, caption: str, users: List[Tuple[int, str]], reply_message, source_message) -> None:
    """Send media broadcast (photo, video, audio, document) to all users."""
    success_count = 0
    failed_count = 0
    
    # Format the caption
    formatted_caption = ""
    if caption:
        formatted_caption = (
            f"<b>#GateHunter | [BROADCAST]</b>\n\n"
            f"{caption}\n\n"
            f"<b>━━━━━━━━━━━━━</b>\n"
            f"Bot by <a href='https://t.me/amkuush'>ªMkUsH</a>"
        )
    
    # Determine the type of media
    media_type = None
    media_file_id = None
    
    if source_message.photo:
        media_type = "photo"
        # Get the largest photo (last in the list)
        media_file_id = source_message.photo[-1].file_id
    elif source_message.video:
        media_type = "video"
        media_file_id = source_message.video.file_id
    elif source_message.audio:
        media_type = "audio"
        media_file_id = source_message.audio.file_id
    elif source_message.document:
        media_type = "document"
        media_file_id = source_message.document.file_id
    elif source_message.voice:
        media_type = "voice"
        media_file_id = source_message.voice.file_id
    elif source_message.animation:
        media_type = "animation"
        media_file_id = source_message.animation.file_id
    elif source_message.sticker:
        media_type = "sticker"
        media_file_id = source_message.sticker.file_id
    elif source_message.video_note:
        media_type = "video_note"
        media_file_id = source_message.video_note.file_id
    else:
        # Fallback to text if no media detected
        media_type = "text"
        if source_message.text:
            text_to_send = source_message.text
            if caption:
                text_to_send = f"{caption}\n\n{text_to_send}"
                
            formatted_text = (
                f"<b>#GateHunter | [BROADCAST]</b>\n\n"
                f"{text_to_send}\n\n"
                f"<b>━━━━━━━━━━━━━</b>\n"
                f"Bot by <a href='https://t.me/amkuush'>ªMkUsH</a>"
            )
        else:
            formatted_text = formatted_caption if formatted_caption else "Broadcast message"
    
    # Broadcast the media to all users
    for user_id, _ in users:
        try:
            if media_type == "photo":
                await bot.send_photo(
                    chat_id=user_id,
                    photo=media_file_id,
                    caption=formatted_caption if formatted_caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif media_type == "video":
                await bot.send_video(
                    chat_id=user_id,
                    video=media_file_id,
                    caption=formatted_caption if formatted_caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif media_type == "audio":
                await bot.send_audio(
                    chat_id=user_id,
                    audio=media_file_id,
                    caption=formatted_caption if formatted_caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif media_type == "document":
                await bot.send_document(
                    chat_id=user_id,
                    document=media_file_id,
                    caption=formatted_caption if formatted_caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif media_type == "voice":
                await bot.send_voice(
                    chat_id=user_id,
                    voice=media_file_id,
                    caption=formatted_caption if formatted_caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif media_type == "animation":
                await bot.send_animation(
                    chat_id=user_id,
                    animation=media_file_id,
                    caption=formatted_caption if formatted_caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif media_type == "sticker":
                await bot.send_sticker(
                    chat_id=user_id,
                    sticker=media_file_id
                )
            elif media_type == "video_note":
                await bot.send_video_note(
                    chat_id=user_id,
                    video_note=media_file_id
                )
            else:
                # Fallback to text
                await bot.send_message(
                    chat_id=user_id,
                    text=formatted_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            
            success_count += 1
        except TelegramError as e:
            logger.error(f"Failed to send media broadcast to user {user_id}: {e}")
            failed_count += 1
        
        # Add a small delay to avoid hitting rate limits
        await asyncio.sleep(0.1)
    
    # Update the original message with results
    media_name = media_type.capitalize() if media_type != "text" else "Message"
    await reply_message.edit_text(
        f"✅ {media_name} Broadcast completed!\n"
        f"• Sent to: {success_count} users\n"
        f"• Failed: {failed_count} users"
    )