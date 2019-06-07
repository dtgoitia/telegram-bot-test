from telegram.ext import CommandHandler


def start_cmd(update, context):  # noqa: D103
    context.message.bot.send_message(chat_id=context.message.chat_id,
                                     text="I'm a bot, please talk to me!")


def hi_cmd(update, context):  # noqa: D103
    user_name = context.message.from_user.first_name
    msg = f"""Hi {user_name}! How are you today?"""
    context.message.bot.send_message(chat_id=context.message.chat_id,
                                     text=msg)


start = CommandHandler('start', start_cmd)
hi = CommandHandler('hi', hi_cmd)
