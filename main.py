"""
Main entry point for the Telegram Store Follow Bot.
"""
import asyncio
import sys
from src.bot import TelegramBot


def main():
    """Run the bot."""
    try:
        bot = TelegramBot()
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
