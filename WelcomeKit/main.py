#!/usr/bin/env python3
# Main entry point for GateHunter Telegram Bot
# Author: Created for @amkuush

import logging
import sys
import asyncio
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    AIORateLimiter
)

# Import configuration
from config import BOT_TOKEN, validate_config

# Import handlers
from handlers.user_commands import (
    start_command, 
    ping_command, 
    cmd_command, 
    gate_command,
    button_callback_handler
)
from handlers.admin_commands import (
    auth_command, 
    deauth_command, 
    list_users_command, 
    list_groups_command, 
    broadcast_command
)

# Import database utilities
from utils.database import init_db

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context) -> None:
    """Handle errors in the dispatcher."""
    logger.error(f"Update {update} caused error {context.error}")

async def handle_dot_commands(update: Update, context) -> None:
    """Handle commands that start with a dot."""
    if not update.message or not update.message.text:
        return
        
    message_text = update.message.text
    command = message_text.split()[0][1:]  # Remove the dot and get the command
    
    # Extract any arguments
    args = message_text.split()[1:]
    context.args = args
    
    # Route to the appropriate command handler
    if command == "gate":
        await gate_command(update, context)
    elif command == "cmd":
        await cmd_command(update, context)
    elif command == "ping":
        await ping_command(update, context)
    elif command == "auth":
        await auth_command(update, context)
    elif command == "deauth":
        await deauth_command(update, context)
    elif command == "listusers":
        await list_users_command(update, context)
    elif command == "listgroup":
        await list_groups_command(update, context)
    elif command == "brod":
        await broadcast_command(update, context)

def main() -> None:
    """Start the bot."""
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    # Initialize the database
    init_db()
    
    # Create the application
    application = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()
    
    # User command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("gate", gate_command))
    application.add_handler(CommandHandler("cmd", cmd_command))
    application.add_handler(CommandHandler("ping", ping_command))
    
    # Admin command handlers
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("deauth", deauth_command))
    application.add_handler(CommandHandler("listusers", list_users_command))
    application.add_handler(CommandHandler("listgroup", list_groups_command))
    application.add_handler(CommandHandler("brod", broadcast_command))
    
    # Dot command handler (commands starting with a dot)
    dot_command_filter = filters.Regex(r'^\.(gate|cmd|ping|auth|deauth|listusers|listgroup|brod)\b')
    application.add_handler(MessageHandler(dot_command_filter, handle_dot_commands))
    
    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    logger.info("Starting GateHunter Telegram Bot")
    print(f"Bot token: {BOT_TOKEN[:5]}...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()