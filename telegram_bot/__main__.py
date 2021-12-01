import logging

from telegram import Update
from telegram.ext import CallbackContext, Dispatcher, Updater

from telegram_bot.commands import start
from telegram_bot.config import get_config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def echo(update: Update, context: CallbackContext) -> None:
    """Echo back to the user with whatever message the user have said to the bot."""
    update.message.reply_markdown_v2(
        text=update.message.text,
    )


def main() -> None:
    config = get_config()

    updater = Updater(token=config.telegram_token)
    dispatcher: Dispatcher = updater.dispatcher  # type: ignore

    # Commands
    dispatcher.add_handler(start)

    # echo_handler = MessageHandler(Filters.text, echo)
    # dispatcher.add_handler(echo_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
