from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram_bot.config import get_config

import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    context.message.bot.send_message(chat_id=context.message.chat_id, text="I'm a bot, please talk to me!")


def echo(update, context):
    context.message.bot.send_message(chat_id=context.message.chat_id, text=context.message.text)


def main() -> None:
    token = get_config('TOKEN')

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
