from datetime import datetime, timedelta, date

import pytz
from ruobr_api import Ruobr, AuthenticationException

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


def get_children_for_user(user: Ruobr) -> dict[int, str] | None:
    """Получить список всех детей пользователя."""
    if user.is_empty:
        return

    children_dict = {}

    if user.is_applicant:  # Обработка родительского аккаунта
        children = user.get_children()
        for i in range(len(children)):
            first_name = children[i]['first_name']
            last_name = children[i]['last_name']
            children_dict[i+1] = f'{first_name} {last_name}'

    return children_dict


def get_child(user: Ruobr, child_number: int = 1) -> Ruobr:
    """Выбрать ребенка пользователя."""
    user.child = child_number - 1  # Выбрать нужного ребёнка
    return user


def homework_for_date(
        user: Ruobr, date_start: date, date_end: date
) -> dict[str, dict[str, list[str]]]:
    """Получить всю домашнюю работу за указанный период."""
    timetable = user.get_timetable(date_start, date_end)
    homeworks = {}

    for obj in timetable:
        date = obj.get('date')
        tasks = obj.get('task')
        subject = obj.get('subject')

        if tasks:
            homework = []
            for task in tasks:
                homework.append(task.get('title'))

            homeworks.setdefault(date, {})[subject] = homework

    return homeworks


def get_homeworks_for_print(homeworks: dict[str, dict[str, list[str]]]) -> str:
    """Возвращает сформированную для вывода строку с домашней работой."""
    str_homeworks = ''

    for date in homeworks:
        str_homeworks += f'\n\n<b>Домашнее задание на {date}:</b>'
        for subject in homeworks[date]:
            str_homeworks += f'\n{subject}: '
            for homework in homeworks[date][subject]:
                str_homeworks += f'{homework} '

    if str_homeworks:
        return str_homeworks
    return 'Ура! домашки нет.'


def timetable_for_date(
    user: Ruobr, date_start: date, date_end: date
) -> dict[str, dict[str, tuple[str]]]:
    """Получить расписание за указанный период."""
    timetable = user.get_timetable(date_start, date_end)
    timetable_date = {}
    for obj in timetable:
        date_ = obj.get('date')
        subject = obj.get('subject')
        time_start = obj.get('time_start')
        time_end = obj.get('time_end')
        timetable_date.setdefault(date_, {})[subject] = (time_start, time_end)
    return timetable_date


def get_timetable_for_print(timetable: dict[str, dict[str, tuple[str]]]) -> str:
    """Возвращает сформированную для вывода строку с расписанием."""
    str_timetable = ''
    for date in timetable:
        str_timetable += f'\n\n<b>Расписание на {date}:</b>'
        for subject in timetable[date]:
            str_timetable += (
                f'\n<i>{timetable[date][subject][0][:5]}'
                f'-{timetable[date][subject][1][:5]}</i> {subject}'
            )
    if str_timetable:
        return str_timetable
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


def get_timetable_tomorrow_date(user: Ruobr) -> dict[str, dict[str, tuple[str]]]:
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


def get_timetable_for_week(user: Ruobr) -> dict[str, dict[str, tuple[str]]]:
    """Получить расписание на неделю."""
    dates = get_date_week()
    return timetable_for_date(user, dates[0], dates[1])


def get_homeworks_for_today(user: Ruobr) -> dict[str, dict[str, list[str]]]:
    """Получить домашнюю работу на сегодня."""
    current_date = get_current_date()
    return homework_for_date(user, current_date, current_date)


def get_timetable_for_today(user: Ruobr) -> dict[str, dict[str, tuple[str]]]:
    """Получить расписание на сегодня."""
    current_date = get_current_date()
    return timetable_for_date(user, current_date, current_date)
