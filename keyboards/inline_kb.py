from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_keyboard(buttons: dict[str, str]) -> InlineKeyboardMarkup:
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for btn in buttons:
        inline_kb.button(
            text=buttons[btn],
            callback_data=btn
        )
    inline_kb.adjust(1)
    return inline_kb.as_markup()
