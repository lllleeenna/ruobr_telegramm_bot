from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder


def create_children_keyboard(children: dict[int, str]) -> InlineKeyboardMarkup:
    children_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for child_id in children:
        children_kb.button(
            text=f'{child_id}: {children[child_id]}',
            callback_data=f'child {child_id} {children[child_id]}',
        )
    children_kb.adjust(1)
    return children_kb.as_markup()
