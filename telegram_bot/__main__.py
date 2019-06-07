from telegram.ext import MessageHandler, Filters, Updater
from telegram_bot.config import get_config
from telegram_bot.commands import hi, start

import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def echo(update, context):
    """Echo back to the user with whatever message the user have said to the bot."""
    context.message.bot.send_message(chat_id=context.message.chat_id,
                                     text=context.message.text)


def main() -> None:  # noqa: D103
    token = get_config('TOKEN')

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    # Commands
    dispatcher.add_handler(start)
    dispatcher.add_handler(hi)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
