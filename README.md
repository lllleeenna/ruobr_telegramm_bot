# Ruobr Telegram Bot
Бот позволяет получать данные из личного кабинета ruobr.ru, выбирать ребенка
из списка, смотреть расписание уроков и домашнее задание.

### Технологии:
- python 3.10
- aiogram 3
- redis
- pydantic

### Файл .env
```
BOT_TOKEN='BOT_TOKEN'
DB_LINK='redis://localhost:6379/0'
```
- TELEGRAM_TOKEN - API Token бота полученный у BotFather
- DB_LINK - путь для подключения к redis

### Запуск проекта
Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:lllleeenna/ruobr_telegramm_bot.git
```
```
cd ruobr_telegramm_bot
```

### Создайте и активируйте виртуальное окружение:
```
python3.10 -m venv venv
```
```
source venv/bin/activate
```

### Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
### Запустите бота
```
python bot.py
```