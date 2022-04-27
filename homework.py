import logging
import os
import sys
import time
from http import HTTPStatus as H
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

import settings

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    handlers=[StreamHandler(stream=sys.stdout)]
)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_message(bot, message):
    """отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Сообщение успешно отправлено')
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """возвращает ответ API, преобразовав его из формата JSON."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            settings.ENDPOINT, headers=settings.HEADERS, params=params
        )
    except Exception as error:
        logging.error(f'Ошибка ответа API: {error}')
        raise Exception(f'Ошибка ответа API: {error}')
    if response.status_code != H.OK:
        logging.error(
            f'Эндпоинт {settings.ENDPOINT} недоступен. '
            f'HTTPStatus is not OK: {response.status_code}')
        raise Exception(
            f'Эндпоинт {settings.ENDPOINT} недоступен. '
            f'HTTPStatus is not OK: {response.status_code}'
        )
    try:
        return response.json()
    except ValueError:
        logging.error('Ошибка формата JSON')
        raise ValueError('Ошибка формата JSON')


def check_response(response):
    """Проверка статуса домашней работы из ответа API."""
    if type(response) is not dict or not response:
        logging.error('Ответ API пуст или отличен от словаря')
        raise TypeError('Ответ API пуст или отличен от словаря')
    if 'homeworks' not in response:
        logging.error('отсутствует ключ "homeworks" в ответе API')
        raise TypeError('отсутствует ключ "homeworks" в ответе API')
    if type(response['homeworks']) is not list:
        logging.error('Ответ API "homeworks" отличин от списка')
        raise TypeError('Ответ API "homeworks" отличин от списка')
    if len(response['homeworks']) == 0:
        logging.error('Список домашних работ пуст')
        raise IndexError('Список домашних работ пуст')

    logging.info('Обновлен статус домешней работы')
    return response['homeworks'][0]


def parse_status(homework):
    """Проверка ключей из ответа API."""
    if 'homework_name' not in homework:
        logging.error('отсутствует ключ "homework_name" в ответе API')
        raise KeyError('отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        logging.error('отсутствует ключ "status" в ответе API')
        raise KeyError('отсутствует ключ "status" в ответе API')

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in settings.HOMEWORK_STATUSES:
        logging.error(
            f'Недокументированный статус "{homework_status}" в ответе API')
        raise Exception(
            f'Недокументированный статус "{homework_status}" в ответе API'
        )
    verdict = settings.HOMEWORK_STATUSES[homework_status]
    logging.info('Получен новый статус.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия переменных окружения."""
    lst = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for index, token in lst.items():
        if token is None:
            logging.critical(
                f'Отсутствует обязательная переменная окружения: {index}'
            )
            return False
    logging.info('Проверка переменных окружения прошла успешно.')
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        exit(logging.critical('Программа принудительно остановлена.'))
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if not bot["id"] or not bot["username"] or not bot["first_name"]:
        logging.critical('Переменная бот не соответствует ожиданию.')
        raise Exception('Переменная бот не соответствует ожиданию.')
    current_timestamp = int(time.time())

    status = ''
    error_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            message = parse_status(check_response(response))

            if message != status:
                send_message(bot, message)
                status = message

        except Exception as error:
            message = f'У меня баги: {error}'
            logging.info(f'Сбой в работе программы: {message}')
            if message != error_message:
                send_message(bot, message)
                error_message = message

        current_timestamp = response.get('current_date')
        time.sleep(settings.RETRY_TIME)


if __name__ == '__main__':
    main()
