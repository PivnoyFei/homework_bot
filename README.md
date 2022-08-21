# Проект homework_bot

## Описание
Бот постоянно будет обращаться к API сервиса Практикум.Домашка и узнавать статус вашей домашней работы, следить за обновлениями статуса домашней работы и уведомляет в случаи его изменения.

### Стек: 
```
Python 3.7, python-telegram-bot.
```

### Запуск проекта:
Клонируем репозиторий и переходим в него:
```bash
git clone https://github.com/PivnoyFei/homework_bot.git
cd homework_bot
```

Создаем и активируем виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```
для Windows
```bash
python -m venv venv
source venv/Scripts/activate
```
```bash
python -m pip install --upgrade pip
```

Ставим зависимости из requirements.txt:
```bash
pip install -r requirements.txt
```

Создаем файл .env, добавьте поочерёдно ключ и значение для каждой переменной:
```bash
PRACTICUM_TOKEN = 'key'
TELEGRAM_TOKEN = 'key'
TELEGRAM_CHAT_ID = 'key'
```

Запускаем проект:
```bash
homework.py
```

### Разработчик проекта
- [Смелов Илья](https://github.com/PivnoyFei)
