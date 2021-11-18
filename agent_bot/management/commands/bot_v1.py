import os
from collections import defaultdict
from django.core.management.base import BaseCommand
# from cake.models import *
# from cake.serve import *
#from self_storage.handlers import order_handler
from django.core.files import File
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Update, user
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Updater, Filters, CallbackContext
from dotenv import load_dotenv
import qrcode
import time

load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')


storage_info = defaultdict()

ADDRESSES = ['⚓️ Адрес 1', '⚓️ Адрес 2', '⚓️ Адрес 3', '⚓️ Адрес 4']
STORAGE_PERIODS = [
    '1 месяц',
    '2 месяца',
    '3 месяца',
    '6 месяцев',
    '12 месяцев',
    'Выбрать другой',
    'Главное меню'
]

CHECKOUT_URL = 'https://www.tinkoff.ru/kassa/solution/qr/'

ADDRESSES_KEYBOARD = ReplyKeyboardMarkup(
    keyboard = [
                [
                    KeyboardButton(text=address),
                ]
                for address in ADDRESSES
            ],
    resize_keyboard=True
)

STORAGE_PERIODS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard = [
                [
                    KeyboardButton(text=period),
                ]
                for period in STORAGE_PERIODS
            ],
    resize_keyboard=True
)

TYPE_STORAGE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard = [
                    [
                        KeyboardButton(text='Сезонные вещи'),
                        KeyboardButton(text='Другое'),
                        KeyboardButton(text='Главное меню'),
                    ]
                ],
                resize_keyboard=True
)


def start(update, context):
    message = update.message
    user_name = message.chat.first_name
    user_id = message.chat_id

    context.bot.send_message(
        chat_id=user_id,
        text=(
            f'Привет, {user_name}.🤚\n\n'
            'Я помогу вам арендовать личную ячейку для хранения вещей.'
            'Давайте посмотрим адреса складов, чтобы выбрать ближайший!'
        ),
        reply_markup=ADDRESSES_KEYBOARD,
    )
    return 1

def select_address(update, context):
    message = update.message
    user_id = message.chat_id

    storage_info[user_id] = {}
    address = message.text
    storage_info[user_id]['address'] = address
    context.bot.send_message(
        chat_id=user_id,
        text='Что хотите хранить?',
        reply_markup=TYPE_STORAGE_KEYBOARD,
    )

    return 2

def select_storage_type(update, context):
    message = update.message
    user_id = message.chat_id

    storage_type = message.text
    storage_info[user_id]['storage_type'] = storage_type

    if storage_type == 'Сезонные вещи':
        return 3
    elif storage_type == 'Другое':
        context.bot.send_message(
            chat_id=user_id,
            text='Выберите желаему площадь ячейки для хранения\n'
                 'Можно выбрать размер от 1 до 10 м2',
            reply_markup=ReplyKeyboardRemove(),
        )
        return 4

    else:
        ConversationHandler.END
        return start(update, context)


def select_storage_cell_size(update, context):
    message = update.message
    user_id = message.chat_id

    cell_size = int(message.text)

    if cell_size in range(1,10):
        price = 599 + 150*(cell_size - 1)
        storage_info[user_id]['cell_size'] = cell_size
        context.bot.send_message(
            chat_id=message.chat_id,
            text=f'Стоимость хранения составит {price} рублей\n'
                 f'Выберите срок хранения',
            reply_markup=STORAGE_PERIODS_KEYBOARD,
        )
        return 6



def select_storage_period(update, context):
    message = update.message
    user_id = message.chat_id

    storage_period = message.text

    if storage_period not in ('Выбрать другой', 'Главное меню'):
        storage_info[user_id]['storage_period'] = storage_period
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Отлично! Теперь вы можете забронировать ячейку',
            reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text='Забронировать')
                        ]
                    ],
                    resize_keyboard=True
            )
        )
        return 7
    elif storage_period == 'Выбрать другой':
      pass

    else:
        ConversationHandler.END
        return start(update, context)


def get_user_data_from_db():
    return False


def is_valid_fio(fio):
    return True


def is_valid_phone(phone):
    return True


def is_valid_passport(passport):
    return True


def is_valid_birth_date(birth_date):
    return True


def get_qr_code(chat_id):
    img = qrcode.make(chat_id)
    img.save(f'{chat_id}.png')
    return f'{chat_id}.png'


def get_user_fio_from_bot(update, context):
    user_info = get_user_data_from_db()
    if not user_info:
        message = update.message
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Пожалуйста, введите ваше ФИО, например - Иванов Иван Иванович',
            reply_markup=ReplyKeyboardRemove()
        )
        return 8


def get_user_phone_from_bot(update, context):
    message = update.message
    fio = message.text
    if is_valid_fio(fio):
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Пожалуйста, введите ваш номер телефона в формате: 79260000000',
            reply_markup=ReplyKeyboardRemove()
        )
        storage_info[message.chat_id]['fio'] = fio
        return 9
    else:
        context.bot.send_message(
            chat_id=message.chat_id,
            text='ФИО введено некорректно! Введите ФИО еще раз, например - Иванов Иван Иванович',
            reply_markup=ReplyKeyboardRemove()
        )
        return 8


def get_user_passport_from_bot(update, context):
    message = update.message
    phone = message.text
    if is_valid_phone(phone):
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Пожалуйста, введите ваши пасспортные данные в формаете СЕРИЯ НОМЕР\n'
                 'Например: 8805 777666',
            reply_markup=ReplyKeyboardRemove()
        )
        storage_info[message.chat_id]['phone'] = phone
        return 10
    else:
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Номер введен некорректно! Введите в формате: 79260000000 ',
            reply_markup=ReplyKeyboardRemove()
        )
        return 9


def get_user_birth_date_from_bot(update, context):
    message = update.message
    passport = message.text
    if is_valid_passport(passport):
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Пожалуйста, введите вашу дату рождения в формете ГОД-МЕСЯЦ-ЧИСЛО\n'
                 'Например: 1991-08-17',
            reply_markup=ReplyKeyboardRemove()
        )
        storage_info[message.chat_id]['passport'] = passport
        return 11
    else:
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Паспортные данные введены некорректно, нужный формат - СЕРИЯ НОМЕР',
            reply_markup=ReplyKeyboardRemove()
        )
        return 10


def create_order(update, context):
    message = update.message
    birth_date = message.text
    if is_valid_birth_date(birth_date):
        storage_info[message.chat_id]['birth_date'] = birth_date
        context.bot.send_message(
            chat_id=message.chat_id,
            text=f'Отлично! Мы получили от вас следующие данные:\n{storage_info[message.chat_id]}',
            reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text='Оплатить'),
                            KeyboardButton(text='Главное меню'),
                        ]
                    ],
                    resize_keyboard=True
            )
        )
        return 12
    else:
        context.bot.send_message(
            chat_id=message.chat_id,
            text='Дата рождения введена некорректно, нужный формат - ГОД-МЕСЯЦ-ЧИСЛО\n'
                 'Например: 1991-08-17',
            reply_markup=ReplyKeyboardRemove()
        )
        return 11


def checkout(update, context):
    message = update.message
    choice = message.text
    if choice == 'Оплатить':
        context.bot.send_message(
            chat_id=message.chat_id,
            text=f'Ссылка на оплату {CHECKOUT_URL}',
            reply_markup=ReplyKeyboardRemove()
        )
        qr_code_path = get_qr_code(message.chat_id)
        time.sleep(2)
        with open(qr_code_path, 'rb') as qr:
            context.bot.send_photo(
                chat_id=message.chat_id,
                photo=qr,
            )

        ConversationHandler.END
        return start(update, context)
    else:
        ConversationHandler.END
        return start(update, context)


def stop(update):
    update.message.reply_text("Стоп")
    return ConversationHandler.END


order_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        1: [MessageHandler(Filters.text, select_address, pass_user_data=True)],
        2: [MessageHandler(Filters.text, select_storage_type, pass_user_data=True)],
        4: [MessageHandler(Filters.text, select_storage_cell_size, pass_user_data=True)],
        5: [MessageHandler(Filters.text, select_storage_cell_size, pass_user_data=True)],
        6: [MessageHandler(Filters.text, select_storage_period, pass_user_data=True)],
        7: [MessageHandler(Filters.text, get_user_fio_from_bot, pass_user_data=True)],
        8: [MessageHandler(Filters.text, get_user_phone_from_bot, pass_user_data=True)],
        9: [MessageHandler(Filters.text, get_user_passport_from_bot, pass_user_data=True)],
        10: [MessageHandler(Filters.text, get_user_birth_date_from_bot, pass_user_data=True)],
        11: [MessageHandler(Filters.text, create_order, pass_user_data=True)],
        12: [MessageHandler(Filters.text, checkout, pass_user_data=True)],
    },

    fallbacks=[CommandHandler('stop', stop)]
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        updater = Updater(token, use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(order_handler)

        updater.start_polling()
        updater.idle()
