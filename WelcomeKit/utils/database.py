#!/usr/bin/env python3
# Database management for the Telegram bot
# Author: Created for @amkuush

import sqlite3
import logging
import json
from typing import List, Tuple, Optional, Dict, Any

from config import DB_FILE, ADMIN_IDS

# Set up logger
logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database, creating tables if they don't exist."""
    conn = None
    try:
        # Create database connection
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create authorized groups table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS authorized_groups (
            group_id INTEGER PRIMARY KEY,
            group_name TEXT NOT NULL,
            authorized_by INTEGER,
            authorized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (authorized_by) REFERENCES users (user_id)
        )
        ''')
        
        # Create scan history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cms TEXT,
            payment_gateways TEXT,
            captcha TEXT,
            cloudflare BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def add_user_to_db(user_id: int, username: str) -> None:
    """Add a user to the database if they don't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", 
            (user_id,)
        )
        if not cursor.fetchone():
            # Insert new user
            cursor.execute(
                "INSERT INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            conn.commit()
            logger.info(f"Added new user: {username} ({user_id})")
    except sqlite3.Error as e:
        logger.error(f"Database error adding user: {e}")
    finally:
        if conn:
            conn.close()

def is_authorized(chat_id: int) -> bool:
    """Check if a chat is authorized to use the bot."""
    # Private chats are always authorized
    if chat_id > 0:
        return True
    
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if group is authorized
        cursor.execute(
            "SELECT group_id FROM authorized_groups WHERE group_id = ?", 
            (chat_id,)
        )
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Database error checking authorization: {e}")
        return False
    finally:
        if conn:
            conn.close()

def authorize_group(group_id: int, group_name: str, authorized_by: int = None) -> None:
    """Authorize a group to use the bot."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if group exists
        cursor.execute(
            "SELECT group_id FROM authorized_groups WHERE group_id = ?", 
            (group_id,)
        )
        if cursor.fetchone():
            # Update existing group
            cursor.execute(
                "UPDATE authorized_groups SET group_name = ?, authorized_by = ? WHERE group_id = ?",
                (group_name, authorized_by, group_id)
            )
        else:
            # Insert new group
            cursor.execute(
                "INSERT INTO authorized_groups (group_id, group_name, authorized_by) VALUES (?, ?, ?)",
                (group_id, group_name, authorized_by)
            )
        
        conn.commit()
        logger.info(f"Authorized group: {group_name} ({group_id})")
    except sqlite3.Error as e:
        logger.error(f"Database error authorizing group: {e}")
    finally:
        if conn:
            conn.close()

def deauthorize_group(group_id: int) -> None:
    """Deauthorize a group."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Delete group
        cursor.execute(
            "DELETE FROM authorized_groups WHERE group_id = ?", 
            (group_id,)
        )
        
        conn.commit()
        logger.info(f"Deauthorized group: {group_id}")
    except sqlite3.Error as e:
        logger.error(f"Database error deauthorizing group: {e}")
    finally:
        if conn:
            conn.close()

def get_all_users() -> List[Tuple[int, str]]:
    """Get all users from the database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, username FROM users ORDER BY first_seen DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error getting users: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_groups() -> List[Tuple[int, str]]:
    """Get all authorized groups from the database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT group_id, group_name FROM authorized_groups ORDER BY authorized_at DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error getting groups: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_scan_to_history(user_id: int, url: str, results: Dict[str, Any]) -> None:
    """Add a scan to the history."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cms = json.dumps(results.get('cms', []))
        payment_gateways = json.dumps(results.get('payment_gateways', []))
        captcha = json.dumps(results.get('captcha', []))
        cloudflare = 1 if results.get('cloudflare') else 0
        
        cursor.execute(
            """
            INSERT INTO scan_history 
            (user_id, url, cms, payment_gateways, captcha, cloudflare) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, url, cms, payment_gateways, captcha, cloudflare)
        )
        
        conn.commit()
        logger.info(f"Added scan history for user {user_id}, URL: {url}")
    except sqlite3.Error as e:
        logger.error(f"Database error adding scan history: {e}")
    finally:
        if conn:
            conn.close()

def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    return user_id in ADMIN_IDS