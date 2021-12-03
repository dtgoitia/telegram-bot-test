import logging
from typing import Callable, List
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext, InlineQueryHandler

from telegram_bot.bots.core import run_bot
from telegram_bot.exercises import AVAILABLE_EXERCISES, Exercise
from telegram_bot.log import DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL
from telegram_bot.search import ExerciseIndex

logger = logging.getLogger(__name__)


def echo(update: Update, context: CallbackContext) -> None:
    """Echo back to the user with whatever message the user have said to the bot."""
    update.message.reply_markdown_v2(
        text=update.message.text,
    )


def start_cmd(update: Update, _: CallbackContext) -> None:
    update.message.reply_markdown_v2(
        text="I'm a bot, please talk to me",
    )
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")


def get_gym_exercises_inline_query_callback(exercises: List[Exercise]) -> Callable:
    indexed_exercises = ExerciseIndex(exercises=exercises)

    def gym_exercises_inline_query(update: Update, _: CallbackContext) -> None:
        query = update.inline_query.query
        logger.debug(f"gym_exercises_inline_query: {query!r}")

        if query == "":
            return

        exercises = indexed_exercises.query(query)

        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=exercise.name,
                input_message_content=InputTextMessageContent(
                    f"```\n{exercise.to_str()}```",
                    parse_mode=ParseMode.MARKDOWN_V2,
                ),
            )
            for exercise in exercises
        ]

        update.inline_query.answer(results)

    return gym_exercises_inline_query


def run_dtg_bot() -> None:
    callback = get_gym_exercises_inline_query_callback(exercises=AVAILABLE_EXERCISES)
    handlers = [
        InlineQueryHandler(callback=callback),
    ]

    run_bot(handlers=handlers)


if __name__ == "__main__":
    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=DEFAULT_LOG_LEVEL)
    run_dtg_bot()
