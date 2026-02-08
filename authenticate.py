#!/usr/bin/env python3
"""
One-time authentication script for Telegram bot.
Run this once to create the bot_session.session file.
"""
import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

if not all([API_ID, API_HASH, PHONE_NUMBER]):
    print("ERROR: Missing API_ID, API_HASH, or PHONE_NUMBER in .env file")
    exit(1)

async def authenticate():
    print(f"🔐 Authenticating as {PHONE_NUMBER}...")
    print("📱 You will receive a code via Telegram. Enter it when prompted.\n")
    
    # Ensure .sessions directory exists
    os.makedirs('.sessions', exist_ok=True)
    
    client = TelegramClient('.sessions/bot_session', int(API_ID), API_HASH)
    
    await client.start(phone=PHONE_NUMBER)
    
    me = await client.get_me()
    print(f"\n✅ Authentication successful!")
    print(f"   Logged in as: {me.first_name} (@{me.username})")
    print(f"   User ID: {me.id}\n")
    print("💾 Session file 'bot_session.session' created!")
    print("🚀 You can now run the bot with: ./docker-helper.sh start\n")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(authenticate())
