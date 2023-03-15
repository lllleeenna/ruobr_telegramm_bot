from aiogram.fsm.state import StatesGroup, State


class StateLogin(StatesGroup):
    GET_USERNAME_PASSWORD = State()
    GET_CHILD = State()
    GET_COMMAND = State()
