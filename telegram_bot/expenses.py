import datetime
import enum
from dataclasses import dataclass
from decimal import Decimal
from pprint import pprint

from telegram import Update
from telegram.ext import CallbackContext, InlineQueryHandler

from telegram_bot.security import is_message_from_bot_owner


class PaymentAccount(enum.Enum):
    monzo = "Assets:Banks:Monzo:Current Account"
    revolut_personal = "Assets:Banks:Revolut:Personal"
    revolut_business = "Assets:Banks:Revolut:HIRU:GBP"
    amex = "Assets:Banks:American Express"
    evo = "Assets:Banks:EVO"


class Currency(enum.Enum):
    GBP = "GBP"
    EUR = "EUR"


@dataclass
class Expense:
    paid_with: PaymentAccount
    amount: Decimal
    currency: Currency
    description: str
    shared: bool

    def to_journal_entry(self) -> str:
        pending = "!" if self.pending else "*"
        lines = [
            f"{datetime.date.today().isoformat()} {pending} {self.description}",
            f"    {self.paid_with.value}  {self.amount} {self.currency.value}",
        ]

        if self.shared:
            lines.append("    ; SHARED")

        entry = "\n".join(lines)
        return entry

    @property
    def pending(self) -> bool:
        return self.paid_with in {PaymentAccount.revolut_business, PaymentAccount.amex}


EXPENSES_CHANNEL_ID = -1001727175476

# InlineQueryCallback = Callable[[Update, CallbackContext], None]


def expenses_inline_callback(update: Update, context: CallbackContext) -> None:
    if not is_message_from_bot_owner(update=update):
        return

    query = update.inline_query.query
    chat_id = update.inline_query.id
    pprint(context.bot)
    pprint(query)
    pprint(chat_id)


expenses_inline_query_handler = InlineQueryHandler(callback=expenses_inline_callback)
