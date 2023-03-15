from typing import Callable

from aiogram import Dispatcher
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ruobr_api import Ruobr

from keyboards.children_kb import create_children_keyboard
from keyboards.inline_kb import create_inline_keyboard
from utils.statelogin import StateLogin
from ruobr.ruobr import (
    get_user_ruobr, get_children_for_user,
    get_homeworks_for_today, get_homeworks_tomorrow_date,
    get_homeworks_for_week, get_homeworks_for_print,
    get_timetable_tomorrow_date, get_timetable_for_today,
    get_timetable_for_week, get_timetable_for_print,
    get_child,
)
from filters.filters import (
    UserRuobr,
    UsernamePasswordInMessage,
)
from lexicon.lexicon import LEXICON, LEXICON_HOMEWORK_KB, LEXICON_SCHEDULE_KB


async def command_start(message: Message, state: FSMContext):
    """Обрабатывает команду /start.
    Приветствует пользователя и запрашивает логин/пароль.
    """
    await state.clear()
    await message.answer(text=LEXICON[message.text])
    await state.set_state(StateLogin.GET_USERNAME_PASSWORD)


async def get_username_password_ruobr(
        message: Message,
        state: FSMContext,
        user: UserRuobr
):
    """Принимает логин и пароль пользователя Rubor."""
    user_ruobr: Ruobr | None = get_user_ruobr(user.username, user.password)
    if user_ruobr:
        await state.update_data(username=user.username, password=user.password)
        await message.answer(text=LEXICON['authentication'])
        if len(get_children_for_user(user_ruobr)) > 1:
            await message.answer(
                text=LEXICON['select_child'],
                reply_markup=create_children_keyboard(
                    get_children_for_user(user_ruobr)
                ),
            )
            await state.set_state(StateLogin.GET_CHILD)
        else:
            await state.update_data(child=1)
            await state.set_state(StateLogin.GET_COMMAND)
    else:
        await message.answer(text=LEXICON['not_authentication'])
        await state.set_state(StateLogin.GET_USERNAME_PASSWORD)


async def command_get_child(message: Message, state: FSMContext):
    """Обрабатывает команду /get_child.
    Предлагает выбрать ребенка из списка.
    """
    context_data = await state.get_data()
    user_ruobr = get_user_ruobr(
        context_data.get('username'),
        context_data.get('password'),
    )

    await message.answer(
        text=LEXICON['authentication'],
        reply_markup=create_children_keyboard(
            get_children_for_user(user_ruobr)
        ),
    )


async def get_selected_child(
        callback: CallbackQuery,
        state: FSMContext,
):
    """Срабатывает на нажатие инлайн-кнопки с ребенком, аутентифицированным
    пользователем.
    """
    child_id = callback.data.split()[1]
    await state.update_data(child=child_id)
    await state.set_state(StateLogin.GET_COMMAND)
    await callback.answer()


async def command_homework(message: Message):
    """Обрабатывает команду /homework."""
    await message.answer(
        text=LEXICON['homework'],
        reply_markup=create_inline_keyboard(LEXICON_HOMEWORK_KB),
    )


async def get_homework(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие инлайн-кнопок с домашней работой.
    Возвращает домашнюю работу за указанный на кнопке период."""
    get_homework: dict[str, Callable[[Ruobr], dict]] = {
        'hw_today': get_homeworks_for_today,
        'hw_tomorrow': get_homeworks_tomorrow_date,
        'hw_week': get_homeworks_for_week,
    }
    context_data = await state.get_data()
    user_ruobr: Ruobr = get_user_ruobr(
        context_data.get('username'),
        context_data.get('password'),
    )
    user_ruobr: Ruobr = get_child(user_ruobr)
    hw: dict = get_homework.get(callback.data)(user_ruobr)
    hw: str = get_homeworks_for_print(hw)

    await callback.message.edit_text(
        text=hw,
        reply_markup=create_inline_keyboard(LEXICON_HOMEWORK_KB),
    )

    await callback.answer()


async def command_schedule(message: Message):
    """Обрабатывает команду /schedule."""
    await message.answer(
        text=LEXICON['schedule'],
        reply_markup=create_inline_keyboard(LEXICON_SCHEDULE_KB),
    )


async def get_schedule(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие инлайн-кнопок с расписанием.
    Возвращает расписание за указанный на кнопке период."""
    get_timetable: dict[str, Callable[[Ruobr], dict]] = {
        'sch_today': get_timetable_for_today,
        'sch_tomorrow': get_timetable_tomorrow_date,
        'sch_week': get_timetable_for_week,
    }
    context_data = await state.get_data()
    user_ruobr = get_user_ruobr(
        context_data.get('username'),
        context_data.get('password'),
    )
    user_ruobr = get_child(user_ruobr)
    timetable: dict = get_timetable.get(callback.data)(user_ruobr)
    timetable: str = get_timetable_for_print(timetable)
    await callback.message.edit_text(
        text=timetable,
        reply_markup=create_inline_keyboard(LEXICON_SCHEDULE_KB),
    )
    await callback.answer()


async def command_help(message: Message):
    """Обрабатывает команду /help."""
    await message.answer(text=LEXICON[message.text])


async def get_command_from_not_authentication(message: Message):
    """Обрабатывает сообщения, если логи и пароль не были введены."""
    await message.answer(text=LEXICON['not_authentication'])


async def get_other_answer(message: Message):
    """Обрабатывает все неизвестные команды."""
    await message.answer(text=LEXICON['other_answer'])


def register_user_handlers(dp: Dispatcher):
    dp.message.register(command_start, Command(commands='start'))
    dp.message.register(
        get_username_password_ruobr,
        StateLogin.GET_USERNAME_PASSWORD,
        UsernamePasswordInMessage(),
    )
    dp.callback_query.register(
        get_selected_child,
        Text(startswith='child'),
    )
    dp.message.register(
        command_get_child,
        Command(commands='get_child'),
        StateLogin.GET_COMMAND,
    )
    dp.message.register(
        command_homework,
        Command(commands='homework'),
        StateLogin.GET_COMMAND,
    )
    dp.callback_query.register(
        get_homework,
        Text(startswith='hw_'),
        StateLogin.GET_COMMAND,
    )
    dp.message.register(
        command_schedule,
        Command(commands='schedule'),
        StateLogin.GET_COMMAND,
    )
    dp.message.register(
        command_help,
        Command(commands='help'),
    )
    dp.callback_query.register(
        get_schedule,
        Text(startswith='sch_'),
        StateLogin.GET_COMMAND,
    )
    dp.message.register(
        get_command_from_not_authentication,
        StateLogin.GET_USERNAME_PASSWORD,
    )
    dp.message.register(get_other_answer)
