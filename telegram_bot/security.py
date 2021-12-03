from telegram import Update

from telegram_bot.config import get_config


def is_message_from_bot_owner(update: Update) -> bool:
    config = get_config()
    user_id = update.inline_query.from_user.id
    owner_id = config.telegram_bot_owner_user_id
    return user_id == owner_id
