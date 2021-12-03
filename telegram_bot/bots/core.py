import logging
from typing import Sequence

from telegram.ext import Dispatcher, Handler, Updater

from telegram_bot.config import get_config

logger = logging.getLogger(__name__)


def run_bot(handlers: Sequence[Handler]) -> None:
    config = get_config()

    updater = Updater(token=config.telegram_token, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher  # type: ignore

    # Add handlers to bot
    for handler in handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()  # I think this spawns threads and carries on (non-blocking)

    updater.idle()  # Wait for a signal to stop bot and gracefully clean up threads
    logger.debug("Bot gracefully stopped")
