from telegram.error import TelegramError
from telegram import Bot
from utils.logging_config import log_json
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID


LOGGER = 'MESSAGE SENDING SUBPROCESS'

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def post_to_telegram_channel(post_text: str) -> None:
    """
    Sends a text message to the configured Telegram channel.

    :param post_text: the message text to be sent.
    :return: None
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    try:
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=post_text, parse_mode='HTML')
        log_json(LOGGER, 'info', 'The subprocess is ended successfully')
    except TelegramError as e:
        log_json(LOGGER, 'error', 'The subprocess is failed', reason='Message sending failure',
                 error=f'{e}')
