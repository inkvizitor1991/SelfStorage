import logging
import time
import telegram
import qrcode

import phonenumbers
from phonenumbers import NumberParseException

from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings

from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

STORAGE, CATEGORY, THINGS, QUANTITY, PERIOD, CHECK_PERIOD, INITIALS, PASPORT, BIRTH, ORDER, CHECKOUT = range(
    11)

storage_info = defaultdict()

CHECKOUT_URL = 'https://www.tinkoff.ru/kassa/solution/qr/'

TG_TOKEN = settings.BOT_TOKEN

bot = telegram.Bot(token=TG_TOKEN)

address_kb = [
    ['Пироговская набережная 15 (м.Площадь Ленина)'],
    ['Московское шоссе, 25, корп. 1В (м.Звездная)'],
    ['ул. Крыленко, 3Б ( м. Улица Дыбенко )'],
    ['Мурино, Воронцовский б-р, 3 ( м. Девяткино )'],
]
choosing_category_kb = [['сезонные вещи', 'другое']]

seasonal_things_kb = [
    ['лыжи', 'сноуборд'],
    ['велосипед', 'колеса']
]
storage_period_kb = [
    ['неделя', 'месяц', 'пол года'],
    ['больше месяца но меньше пол года']
]
more_storage_period_kb = [
    ['2 месяца', '3 месяца'],
    ['4 месяца', '5 месяцев'],
    ['назад']
]
tires_storage_period_kb = [
    ['месяц', 'пол года'],
    ['больше месяца но меньше пол года']
]
byu_or_menu_kb = [['Оплатить', 'Главное меню']]

address = ReplyKeyboardMarkup(
    address_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)

choosing_category = ReplyKeyboardMarkup(
    choosing_category_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
seasonal_things = ReplyKeyboardMarkup(
    seasonal_things_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
storage_period = ReplyKeyboardMarkup(
    storage_period_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
more_storage_period = ReplyKeyboardMarkup(
    more_storage_period_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)

tires_storage_period = ReplyKeyboardMarkup(
    tires_storage_period_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)

byu_or_menu = ReplyKeyboardMarkup(
    byu_or_menu_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)


def get_user_data_from_db():
    return False


def is_valid_fio(fio):
    return True


def is_valid_phone(phonenumber):
        try:
            number = phonenumbers.parse(phonenumber, 'RU')
            if phonenumbers.is_valid_number(number):
                phone = phonenumbers.format_number(
                    number,
                    phonenumbers.PhoneNumberFormat.E164
                )
                return True
        except NumberParseException:
            return False


def is_valid_passport(passport):
    return True


def is_valid_birth_date(birth_date):
    return True


def get_qr_code(chat_id):
    img = qrcode.make(chat_id)
    img.save(f'{chat_id}.png')
    return f'{chat_id}.png'


def start(update, context):
    time.sleep(0.5)
    message = update.message
    user_name = message.chat.first_name
    text = f'Привет, {user_name}.🤚\n\n' \
           'Я помогу вам арендовать личную ячейку для хранения вещей.' \
           'Давайте посмотрим адреса складов, чтобы выбрать ближайший!'
    update.message.reply_text(text)
    time.sleep(1)
    reply_text = 'Выберите склад, для хранения вещей.'
    update.message.reply_text(reply_text, reply_markup=address)
    time.sleep(0.2)
    return STORAGE


def get_storage(update, context):
    message = update.message
    user_id = message.chat_id
    storage_info[user_id] = {}
    address = message.text
    storage_info[user_id]['address'] = address
    reply_text = 'Что хотите хранить?'
    update.message.reply_text(reply_text, reply_markup=choosing_category)
    return CATEGORY


def choose_category(update, context):
    message = update.message
    user_id = message.chat_id

    storage_type = message.text
    storage_info[user_id]['storage_type'] = storage_type
    if storage_type == 'другое':
        print('ок')
    if storage_type == 'сезонные вещи':
        reply_text = 'Выберете вещи.'
        update.message.reply_text(reply_text, reply_markup=seasonal_things)
        return THINGS


def get_things(update, context):
    message = update.message
    user_id = message.chat_id
    things = message.text
    storage_info[user_id]['things'] = things
    update.message.reply_text('Укажите кол-во.')
    return QUANTITY


def get_quantity(update, context):
    message = update.message
    user_id = message.chat_id
    cell_size = message.text
    if cell_size.isdigit() and int(cell_size) < 100:
        context.user_data['quantity'] = cell_size
        update.message.reply_text('Стоимость: 10000 за месяц')
        storage_info[user_id]['cell_size'] = cell_size
        time.sleep(0.3)
        things = storage_info[user_id].get('things')
        if things in ('лыжи', 'сноуборд', 'велосипед'):
            reply_text = 'Выберете срок хранения.'
            update.message.reply_text(reply_text, reply_markup=storage_period)
            return PERIOD
        if things == 'колеса':
            reply_text = 'Выберете срок хранения.'
            update.message.reply_text(
                reply_text,
                reply_markup=tires_storage_period
            )
            return PERIOD

    else:
        update.message.reply_text('Проверьте правильность ввода.')


def get_storage_period(update, context):
    message = update.message
    user_id = message.chat_id

    storage_period = message.text
    if storage_period == 'больше месяца но меньше пол года':
        update.message.reply_text('Принято.', reply_markup=more_storage_period)
        return CHECK_PERIOD
    else:
        storage_info[user_id]['storage_period'] = storage_period
        user_info = get_user_data_from_db()
        ####Если есть пользователь в бд сразу на оплату
        if not user_info:
            update.message.reply_text(
                'Пожалуйста, введите ваше ФИО, например - Иванов Иван Иванович',
            )
            return INITIALS


def check_storage_period(update, context):
    message = update.message
    user_id = message.chat_id
    user_message = message.text
    things = storage_info[user_id].get('things')

    if things in ('лыжи', 'сноуборд', 'велосипед') and user_message == 'назад':
        reply_text = 'Выберете срок хранения.'
        update.message.reply_text(reply_text, reply_markup=storage_period)
        return PERIOD
    if things == 'колеса' and user_message == 'назад':
        reply_text = 'Выберете срок хранения.'
        update.message.reply_text(
            reply_text,
            reply_markup=tires_storage_period
        )
        return PERIOD
    else:
        storage_info[user_id]['storage_period'] = user_message
        user_info = get_user_data_from_db()
        ####Если есть сразу на оплату
        if not user_info:
            update.message.reply_text(
                'Пожалуйста, введите ваше ФИО, например - Иванов Иван Иванович',
            )
            return INITIALS
        return ORDER


def get_initials(update, context):
    user_message = update.message.text
    message = update.message
    fio = message.text
    if is_valid_fio(user_message):
        update.message.reply_text(
            'Пожалуйста, введите ваш номер телефона в формате: 79260000000'
        )
        storage_info[message.chat_id]['fio'] = fio
        return PASPORT
    else:
        update.message.reply_text(
            'ФИО введено некорректно! Введите ФИО еще раз, например - Иванов Иван Иванович',
        )


def get_user_passport_from_bot(update, context):
    message = update.message
    phone = message.text
    if is_valid_phone(phone):
        update.message.reply_text(
            'Пожалуйста, введите ваши пасспортные данные в формаете СЕРИЯ НОМЕР\n'
            'Например: 8805 777666',
        )
        storage_info[message.chat_id]['phone'] = phone
        return BIRTH
    else:
        update.message.reply_text(
            'Номер введен некорректно! Введите в формате: 79260000000 ',
        )


def get_user_birth_date_from_bot(update, context):
    message = update.message
    passport = message.text
    if is_valid_passport(passport):
        update.message.reply_text(
            'Пожалуйста, введите вашу дату рождения в формете ГОД-МЕСЯЦ-ЧИСЛО\n'
        )
        storage_info[message.chat_id]['passport'] = passport
        return ORDER
    else:
        update.message.reply_text(
            'Паспортные данные введены некорректно, нужный формат - СЕРИЯ НОМЕР',
        )


def create_order(update, context):
    message = update.message
    birth_date = message.text
    user_id = message.chat_id
    storage_type = storage_info[user_id]['storage_type']
    address = storage_info[user_id]['address']
    things = storage_info[user_id]['things']
    period = storage_info[user_id]['storage_period']
    fio = storage_info[message.chat_id]['fio']
    passport = storage_info[message.chat_id]['passport']
    phone = storage_info[message.chat_id]['phone']
    if is_valid_birth_date(birth_date):
        update.message.reply_text(
            f'Отлично! Мы получили от вас следующие данные:\nФИО: {fio}\nПаспортные данные: {passport},\nТелефон: {phone},\nАдрес хранения: {address},\nТип хранения: {storage_type},\nВещь: {things},\nПериод хранения: {period}',
            reply_markup=byu_or_menu
        )
        return CHECKOUT
    else:
        update.message.reply_text(
            'Дата рождения введена некорректно, нужный формат - ГОД-МЕСЯЦ-ЧИСЛО\n'
            'Например: 1991-08-17',
        )


def checkout(update, context):
    message = update.message
    choice = message.text
    if choice == 'Оплатить':
        update.message.reply_text(
            f'Ссылка на оплату {CHECKOUT_URL}'
        )
        qr_code_path = get_qr_code(message.chat_id)
        time.sleep(2)
        with open(qr_code_path, 'rb') as qr:
            context.bot.send_photo(
                chat_id=message.chat_id,
                photo=qr,
            )
        time.sleep(2)
        return start(update, context)
    else:
        return start(update, context)


def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
    )
    return ConversationHandler.END


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = Updater(TG_TOKEN, use_context=True)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={
                STORAGE: [CommandHandler('start', start),
                          MessageHandler(Filters.text, get_storage)],

                CATEGORY: [CommandHandler('start', start),
                           MessageHandler(Filters.text, choose_category)],

                THINGS: [CommandHandler('start', start),
                         MessageHandler(Filters.text, get_things)],

                QUANTITY: [CommandHandler('start', start),
                           MessageHandler(Filters.text, get_quantity)],

                PERIOD: [CommandHandler('start', start),
                         MessageHandler(Filters.text, get_storage_period)],

                CHECK_PERIOD: [CommandHandler('start', start),
                               MessageHandler(Filters.text,
                                              check_storage_period)],

                INITIALS: [CommandHandler('start', start),
                           MessageHandler(Filters.text, get_initials)],

                PASPORT: [CommandHandler('start', start),
                          MessageHandler(Filters.text,
                                         get_user_passport_from_bot)],

                BIRTH: [CommandHandler('start', start),
                        MessageHandler(Filters.text,
                                       get_user_birth_date_from_bot)],

                ORDER: [CommandHandler('start', start),
                        MessageHandler(Filters.text,
                                       create_order)],

                CHECKOUT: [CommandHandler('start', start),
                           MessageHandler(Filters.text,
                                          checkout)],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
