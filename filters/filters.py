from collections import namedtuple

from aiogram.filters import BaseFilter
from aiogram.types import Message

UserRuobr = namedtuple('UserRuobr', ['username', 'password'])


class UsernamePasswordInMessage(BaseFilter):
    async def __call__(
            self, message: Message
    ) -> bool | dict[str, UserRuobr]:
        if len(message.text.split()) == 2:
            username, password = message.text.strip().split()
            return {'user': UserRuobr(username, password)}
        return False
