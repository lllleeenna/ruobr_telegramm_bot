from datetime import datetime, timedelta, date

import pytz
from ruobr_api import Ruobr, AuthenticationException

from ruobr.ruobr_cls import Child, Subject
from ruobr.ruobr_exception import RuobrIsEmptyError, RuobrIsApplicantError

TIMEZONE = 'Asia/Krasnoyarsk'
SATURDAY_NUM = 5
SUNDAY_NUM = 6


def get_user_ruobr(username: str, password: str) -> Ruobr | None:
    """Получить авторизованного на ruobr пользователя."""
    user: Ruobr = Ruobr(username, password)
    try:
        user.get_user()
        return user
    except AuthenticationException:
        return


def get_children_for_user(user: Ruobr) -> dict[int, str]:
    """Получить список всех детей пользователя."""
    if user.is_empty:
        raise RuobrIsEmptyError('На аккаунте не обнаружено детей.')

    if user.is_applicant:  # Обработка родительского аккаунта
        children = [Child(**child) for child in user.get_children()]
        return {
            ind + 1: f'{child.first_name} {child.last_name}'
            for ind, child in enumerate(children)
        }
    else:
        raise RuobrIsApplicantError('Профиль не является родительским.')


def get_child(user: Ruobr, child_number: int = 1) -> Ruobr:
    """Выбрать ребенка пользователя."""
    user.child = child_number - 1  # Выбрать нужного ребёнка
    return user


def homework_for_date(
        user: Ruobr, date_start: date, date_end: date
) -> dict[str, dict[str, list[str]]]:
    """Получить всю домашнюю работу за указанный период."""
    timetable = user.get_timetable(date_start, date_end)
    subjects = [Subject(**subject) for subject in timetable]
    homeworks = {}
    for subject in subjects:
        if subject.task:
            homework = [task.title for task in subject.task]
            homeworks.setdefault(subject.date, {})[subject.subject] = homework
    return homeworks


def get_homeworks_for_print(homeworks: dict[str, dict[str, list[str]]]) -> str:
    """Возвращает сформированную для вывода строку с домашней работой."""
    hw_for_print = ''

    for date in homeworks:
        hw_for_print += f'\n\nДомашнее задание на {date}:'
        for subject in homeworks[date]:
            hw_for_print += f'\n{subject}: '
            hw_for_print += ' '.join(homeworks[date][subject])

    if hw_for_print:
        return hw_for_print
    return 'Ура! домашки нет.'


def timetable_for_date(
        user: Ruobr, date_start: date, date_end: date
) -> dict[str, dict[str, tuple[str, str]]]:
    """Получить расписание за указанный период."""
    timetable = user.get_timetable(date_start, date_end)
    subjects = [Subject(**subject) for subject in timetable]
    timetable_date = {}
    for subject in subjects:
        timetable_date.setdefault(subject.date, {})[subject.subject] = (
            subject.time_start, subject.time_end
        )
    return timetable_date


def get_timetable_for_print(timetable: dict[str, dict[str, tuple[str]]]) -> str:
    """Возвращает сформированную для вывода строку с расписанием."""
    timetable_for_print = ''
    for date in timetable:
        timetable_for_print += f'\n\nРасписание на {date}:'
        for subject in timetable[date]:
            timetable_for_print += (
                f'\n{timetable[date][subject][0][:5]}'
                f'-{timetable[date][subject][1][:5]} {subject}'
            )
    if timetable_for_print:
        return timetable_for_print
    return 'На указанные даты расписания нет!'


def get_current_date() -> date:
    """Текущая дата в указанной тайм-зоне."""
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz).date()


def get_tomorrow_date() -> date:
    """Получить завтрашнюю дату."""
    current_date = get_current_date()
    return current_date + timedelta(days=1)


def get_homeworks_tomorrow_date(user: Ruobr) -> dict[str, dict[str, list[str]]]:
    """Получить домашнюю работу на завтра."""
    tomorrow_date = get_tomorrow_date()
    return homework_for_date(user, tomorrow_date, tomorrow_date)


def get_timetable_tomorrow_date(
        user: Ruobr
) -> dict[str, dict[str, tuple[str, str]]]:
    """Получить расписание на завтра."""
    tomorrow_date = get_tomorrow_date()
    return timetable_for_date(user, tomorrow_date, tomorrow_date)


def get_date_week() -> tuple[date, date]:
    """Получить дату с завтрашнего дня и до конца недели.
    Или если сегодня выходной, то дату начала и конца следующей недели.
    """
    current_date = get_current_date()
    current_weekday = current_date.weekday()
    if current_weekday in (SATURDAY_NUM, SUNDAY_NUM):
        start_date: date = (
            current_date + timedelta(SUNDAY_NUM - current_weekday + 1)
        )
        end_date: date = (
            current_date
            + timedelta(SUNDAY_NUM - current_weekday + SUNDAY_NUM + 1)
        )
        return start_date, end_date
    start_date = current_date + timedelta(days=1)
    end_date = current_date + timedelta(days=SUNDAY_NUM-current_weekday)
    return start_date, end_date


def get_homeworks_for_week(user: Ruobr) -> dict[str, dict[str, list[str]]]:
    """Получить домашнюю работу на неделю."""
    dates: tuple[date, date] = get_date_week()
    return homework_for_date(user, dates[0], dates[1])


def get_timetable_for_week(user: Ruobr) -> dict[str, dict[str, tuple[str, str]]]:
    """Получить расписание на неделю."""
    dates = get_date_week()
    return timetable_for_date(user, dates[0], dates[1])


def get_homeworks_for_today(user: Ruobr) -> dict[str, dict[str, list[str]]]:
    """Получить домашнюю работу на сегодня."""
    current_date = get_current_date()
    return homework_for_date(user, current_date, current_date)


def get_timetable_for_today(user: Ruobr) -> dict[str, dict[str, tuple[str, str]]]:
    """Получить расписание на сегодня."""
    current_date = get_current_date()
    return timetable_for_date(user, current_date, current_date)
