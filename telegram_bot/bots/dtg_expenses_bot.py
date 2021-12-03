import enum
import logging
from decimal import Decimal
from typing import Optional

import attr
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from telegram_bot.bots.core import run_bot
from telegram_bot.expenses import Currency, Expense, PaymentAccount
from telegram_bot.log import DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL

logger = logging.getLogger(__name__)


class Stage(enum.Enum):  # Stage in the chat flow
    selecting_payment_amount = 0
    typing_paid_amount = 1
    selecting_currency = 2
    selecting_if_payment_is_shared = 3
    end = 4


class Key(enum.Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    CLEAR = 10
    OK = 11
    COMMA = 12


@attr.s(auto_attribs=True, frozen=True)
class ConversationState:
    stage: Stage
    payment_account: Optional[PaymentAccount] = None
    amount: Optional[Decimal] = None
    pressed_keys: Optional[str] = None
    currency: Optional[Currency] = None
    description: Optional[str] = None
    shared: Optional[bool] = None


_CACHED_KEYBOARD = None


def build_numeric_inline_keyboard() -> InlineKeyboardMarkup:
    global _CACHED_KEYBOARD
    if _CACHED_KEYBOARD:
        return _CACHED_KEYBOARD

    def add_key(key: Key) -> InlineKeyboardButton:
        _special_keys = {
            Key.CLEAR: "C",
            Key.OK: "OK",
            Key.COMMA: ".",
        }
        text = _special_keys.get(key, str(key.value))
        return InlineKeyboardButton(text, callback_data=key.name)

    keyboard_buttons = [
        [add_key(Key.ONE), add_key(Key.TWO), add_key(Key.THREE)],
        [add_key(Key.FOUR), add_key(Key.FIVE), add_key(Key.SIX)],
        [add_key(Key.SEVEN), add_key(Key.EIGHT), add_key(Key.NINE)],
        [add_key(Key.CLEAR), add_key(Key.COMMA), add_key(Key.ZERO)],
        [add_key(Key.OK)],
    ]
    inline_keyboard = InlineKeyboardMarkup(keyboard_buttons)
    return inline_keyboard


def build_currency_choices() -> InlineKeyboardMarkup:
    used_currencies = ("EUR", "GBP")  # purpose: to list currencies in a specific order

    all_currencies = {currency.value for currency in Currency}
    assert all_currencies == set(used_currencies), "You forgot to use all currencies ;)"

    buttons = [
        [
            InlineKeyboardButton(currency, callback_data=currency)
            for currency in used_currencies
        ]
    ]
    currency_choices = InlineKeyboardMarkup(buttons)

    return currency_choices


class AddExpenseFlow:
    def __init__(self) -> None:
        self._reset_state()

    def _next_state(self, **kwargs):
        logger.debug(f"Updating state to: {kwargs!r}")
        self.state = attr.evolve(self.state, **kwargs)

    def _reset_state(self) -> None:
        logger.debug("Cleaning flow state")
        self.state = ConversationState(stage=Stage.selecting_payment_amount)

    def start_conversation_flow(self, update: Update, context: CallbackContext) -> None:
        self._reset_state()
        logger.info(f"Starting {self.__class__.__name__}")
        accounts = ((account.name, account.value) for account in PaymentAccount)
        keyboard = [
            [
                InlineKeyboardButton(short_name, callback_data=full_name),
            ]
            for short_name, full_name in accounts
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("What have you paid with", reply_markup=reply_markup)

    def handle_user_responses(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        response_payload = query.data
        stage = self.state.stage
        logger.debug(f"Stage: #{stage.value} {stage.name}")
        logger.debug(f"User response payload: {response_payload!r}")

        if stage == Stage.selecting_payment_amount:
            account = PaymentAccount(response_payload)
            self._pick_payment_account(account=account)
            self._change_stage(to=Stage.typing_paid_amount)
            self._ask_user_to_input_paid_amount(query=query)
            return

        if stage == Stage.typing_paid_amount:
            pressed_key = Key[response_payload]
            stage = self._press_amount_key(key=pressed_key)
            if stage == Stage.typing_paid_amount:
                self._ask_user_to_input_paid_amount(query=query)
            elif stage == Stage.selecting_currency:
                self._ask_user_to_select_currency(query=query)
            else:
                logger.warning(f"stage={stage}")
                raise NotImplementedError("I didn't expect to reach this state :S")
            # Do not return here, when you press OK the flow show carry on

        if stage == Stage.selecting_currency:
            currency = Currency(response_payload)
            self._pick_currency(currency=currency)
            self._change_stage(to=Stage.selecting_if_payment_is_shared)
            self._ask_user_to_select_if_payment_is_shared(query=query)
            return

        if stage == Stage.selecting_if_payment_is_shared:
            is_shared = response_payload == "true"
            self._set_is_shared(is_shared=is_shared)
            self._change_stage(to=Stage.end)
            self._create_expense_entry(query=query)
            return

    def _change_stage(self, to: Stage) -> None:
        _from = self.state.stage
        logger.info(f"Changing stage: {_from.name} --> {to.name}")
        self._next_state(stage=to)

    def _pick_payment_account(self, account: PaymentAccount) -> None:
        logger.debug(f"User picked account: {account}")
        self._next_state(payment_account=account)

    def _ask_user_to_input_paid_amount(self, query: CallbackQuery) -> None:
        account = self.state.payment_account
        assert account

        user_input = self.state.pressed_keys
        fmt_user_input = "" if user_input is None else str(user_input)

        message = f"{account.value}\nHow much did you pay?  {fmt_user_input}"
        query.edit_message_text(message, reply_markup=build_numeric_inline_keyboard())

    def _press_amount_key(self, key: Key) -> Stage:
        logger.debug(f"User pressed key: {key}")
        pressed_keys = self.state.pressed_keys
        if key == Key.OK:
            if pressed_keys is None:
                # the user has pressed "OK" without pressing any number before
                return self.state.stage

            amount = Decimal(pressed_keys)
            self._next_state(amount=amount)
            next_stage = Stage.selecting_currency
            self._change_stage(to=next_stage)
            return next_stage

        if key == Key.CLEAR:
            updated_characters = None
        else:
            previous_characters = ""
            if pressed_keys:
                previous_characters = pressed_keys

            character = str(key.value)
            if key == Key.COMMA:
                character = "."
            updated_characters = f"{previous_characters}{character}"

        self._next_state(pressed_keys=updated_characters)
        return self.state.stage

    def _ask_user_to_select_currency(self, query: CallbackQuery) -> None:
        logger.info("Asking user to pick the currency used for the payment")
        assert self.state.payment_account
        message = "\n".join(
            [
                f"Account: {self.state.payment_account.value}",
                f"Amount: {self.state.amount}",
                "In which currency?",
            ]
        )
        query.edit_message_text(message, reply_markup=build_currency_choices())

    def _pick_currency(self, currency: Currency) -> None:
        logger.debug(f"User picked currency: {currency}")
        self._next_state(currency=currency)

    def _ask_user_to_select_if_payment_is_shared(self, query: CallbackQuery) -> None:
        logger.info("Asking user if the payment is shared")
        assert self.state.payment_account
        assert self.state.currency
        message = "\n".join(
            [
                f"Account: {self.state.payment_account.value}",
                f"Amount: {self.state.amount} {self.state.currency.value}",
                "Is this a shared payment?",
            ]
        )
        choices = [
            [
                InlineKeyboardButton("No", callback_data="false"),
                InlineKeyboardButton("Yes", callback_data="true"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(choices)
        query.edit_message_text(message, reply_markup=reply_markup)

    def _set_is_shared(self, is_shared: bool) -> None:
        fmt_is_shared = "shared" if is_shared else "not shared"
        logger.debug(f"User said the payment is {fmt_is_shared}")
        self._next_state(shared=is_shared)

    def _create_expense_entry(self, query: CallbackQuery) -> None:
        logger.debug("Creating journal entry with expense")
        state = self.state
        assert state.payment_account
        assert state.amount
        assert state.currency
        assert state.shared is not None
        expense = Expense(
            paid_with=state.payment_account,
            amount=state.amount,
            currency=state.currency,
            shared=state.shared,
            description="??",
        )
        journal_entry = expense.to_journal_entry()
        journal_entry_as_markdown = f"```\n{journal_entry}```"
        query.edit_message_text(
            journal_entry_as_markdown,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


def run_dtg_expenses_bot() -> None:
    flow = AddExpenseFlow()
    handlers = [
        CommandHandler(
            command="add_expense",
            callback=flow.start_conversation_flow,
        ),
        CallbackQueryHandler(flow.handle_user_responses),
        # InlineQueryHandler(callback=show_commands_inline_query_callback),
    ]

    run_bot(handlers=handlers)


if __name__ == "__main__":
    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=DEFAULT_LOG_LEVEL)
    run_dtg_expenses_bot()
