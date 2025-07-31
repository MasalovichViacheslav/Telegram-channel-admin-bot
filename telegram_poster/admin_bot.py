from dotenv import load_dotenv
import os
from telegram.error import TelegramError
from telegram import Bot


# Load variable from .env file
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID=os.getenv('TELEGRAM_CHANNEL_ID')

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def post_to_telegram_channel(post_text: str) -> None:
    """
    Sends a text message to the configured Telegram channel.

    :param post_text: the message text to be sent.
    :return: None
    """
    try:
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=post_text, parse_mode='HTML')
    except TelegramError as e:
        print(f"Message sending failure: {e}")
