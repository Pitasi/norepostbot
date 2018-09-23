from os import getenv
import logging
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from src.handlers import (
    url_handler, text_link_handler, forwarded_handler, photo_handler, delete_handler
)


# Get config from env. variables
TOKEN = getenv('TOKEN')
WEBHOOK_URL = getenv('WEBHOOK_URL', False)
if WEBHOOK_URL and WEBHOOK_URL[-1] != '/':
    WEBHOOK_URL += '/'


# Init logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('delete', delete_handler))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))
    dp.add_handler(MessageHandler(Filters.entity("url"), url_handler))
    dp.add_handler(
        MessageHandler(Filters.entity("text_link"), text_link_handler)
    )
    dp.add_handler(MessageHandler(Filters.caption_entity("url"), url_handler))
    dp.add_handler(
        MessageHandler(Filters.caption_entity("text_link"), text_link_handler)
    )
    dp.add_handler(MessageHandler(Filters.forwarded, forwarded_handler))

    dp.add_error_handler(error)

    # Start
    if WEBHOOK_URL:
        logger.info("Running in webhook mode")
        updater.start_webhook(listen="0.0.0.0", port=443, url_path=TOKEN)
        updater.bot.set_webhook(WEBHOOK_URL + TOKEN)
    else:
        logger.info("Running in long-polling mode")
        updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
