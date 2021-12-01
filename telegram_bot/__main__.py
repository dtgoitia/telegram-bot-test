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
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    InlineQueryHandler,
    Updater,
)
from telegram.utils.helpers import escape_markdown

from telegram_bot.config import get_config
from telegram_bot.exercises import AVAILABLE_EXERCISES, Exercise
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


def gym_exercises_inline_query_factory(exercises: List[Exercise]) -> Callable:
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
                    f"```{exercise.to_str()}```",
                    parse_mode=ParseMode.MARKDOWN_V2,
                ),
            )
            for exercise in exercises
        ]

        update.inline_query.answer(results)

    return gym_exercises_inline_query


def inlinequery(update: Update, _: CallbackContext) -> None:
    """Handle the inline query."""
    logger.debug(update)
    query = update.inline_query.query
    logger.info(f"query = {query!r}")

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            # id=str(uuid4()),
            id="1",
            title="test",
            input_message_content=InputTextMessageContent("this is a message"),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]

    update.inline_query.answer(results)


def main() -> None:
    config = get_config()

    updater = Updater(token=config.telegram_token)
    dispatcher: Dispatcher = updater.dispatcher  # type: ignore

    # Commands
    dispatcher.add_handler(CommandHandler("start", start_cmd))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(
        InlineQueryHandler(
            gym_exercises_inline_query_factory(exercises=AVAILABLE_EXERCISES)
        )
    )

    updater.start_polling()


if __name__ == "__main__":
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    logger.debug("Running main function")
    main()
