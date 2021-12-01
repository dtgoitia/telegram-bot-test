from telegram import Update
from telegram.ext import CallbackContext, CommandHandler


def start_cmd(update: Update, context: CallbackContext) -> None:
    update.message.reply_markdown_v2(
        text="I'm a bot, please talk to me",
    )


start = CommandHandler("start", start_cmd)
