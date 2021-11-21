import logging
import time
from datetime import datetime, timedelta
import telegram
import qrcode

import phonenumbers
from phonenumbers import NumberParseException

from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from agent_bot.models import Profile, Stuff, Stuff_categories, Order, Promo_code

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

SELECTION, STORAGE, CATEGORY, CELL_SIZE, SELECT_SIZE,SELECT_CELL_SIZE, THINGS, QUANTITY, PERIOD, CHECK_PERIOD, RESERVE, INITIALS, PASPORT, BIRTH, ORDER, CHECKOUT, MENU = range(
    17)

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
    ['1 неделя', '1 месяц', '6 месяцев'],
    ['меньше месяца, но больше недели'],
    ['больше месяца, но менее полугода']
]
less_month_storage_period_kb = [
    ['2 недели', '3 недели'],
    ['назад']
]
more_storage_period_kb = [
    ['2 месяца', '3 месяца'],
    ['4 месяца', '5 месяцев'],
    ['назад']
]
tires_storage_period_kb = [
    ['1 месяц', '6 месяцев', '12 месяцев'],
    ['больше месяца, но менее полугода'],
    ['больше 6 месяцев, но менее года']
]
more_6_months_storage_period_kb = [
    ['7 месяцев', '8 месяцев'],
    ['9 месяцев','10 месяцев'],
    ['11 месяцев'],
    ['назад']
]
byu_or_menu_kb = [['Оплатить', 'Главное меню']]

reserve_kb = [['Зарезервировать', 'Главное меню']]

your_orders_kb = [['Мои ячейки', 'Создать новую ячейку']]

new_order_kb = [['Создать новую ячейку']]

other_things_kb = [
    ['1', '2', '3', '4', '5'],
    ['6', '7', '8', '9', '10']
]

menu_kb = [['Главное меню']]

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
more_6_months_storage_period = ReplyKeyboardMarkup(
    more_6_months_storage_period_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
less_month_storage_period = ReplyKeyboardMarkup(
    less_month_storage_period_kb,
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
reserve = ReplyKeyboardMarkup(
    reserve_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
your_orders = ReplyKeyboardMarkup(
    your_orders_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
new_order = ReplyKeyboardMarkup(
    new_order_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
other_things = ReplyKeyboardMarkup(
    other_things_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)
menu = ReplyKeyboardMarkup(
    menu_kb,
    resize_keyboard=True,
    one_time_keyboard=True
)


def is_valid_fio(fio):
    fio_splitted = fio.split()
    if len(fio_splitted) != 3:
        return False
    elif all([fio_item.isalpha() for fio_item in fio_splitted]):
        return True
    else:
        return False


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
    passport_splitted = passport.split()
    if len(passport_splitted) != 2:
        return False
    series, num = passport_splitted
    if not all([series.isdigit(), num.isdigit()]):
        return False
    elif len(series) == 4 and len(num) == 6:
        return True
    else:
        return False


def is_valid_birth_date(birth_date):
    try:
        datetime.strptime(birth_date, '%Y-%m-%d')
        return True
    except Exception:
        return False


def get_qr_code(chat_id):
    img = qrcode.make(chat_id)
    img.save(f'{chat_id}.png')
    return f'{chat_id}.png'


def get_storage_interval_timedelta(period):
    amount, interval = period.split()
    if interval.startswith('н'):
        days = 7 * int(amount)
        delta = timedelta(days=days)
        return delta
    elif interval.startswith('м'):
        days = 30 * int(amount)
        delta = timedelta(days=days)
        return delta


def get_user_data_from_db(update):
    try:
        message = update.message
        user_id = message.chat_id
        existing_user = Profile.objects.get(tg_chat_id=user_id)
        if existing_user:
            return True
    except:
        return False


def is_orders(update):
    try:
        message = update.message
        user_id = message.chat_id
        if {Order.objects.filter(profile__tg_chat_id__contains=user_id)}:
            return your_orders
        else:
            return new_order
    except:
        return new_order


def start(update, context):
    time.sleep(0.5)
    message = update.message
    user_name = message.chat.first_name
    user_info = get_user_data_from_db(update)
    if not user_info:
        text = f'Привет, {user_name}.🤚\n\n' \
               'Я помогу вам арендовать личную ячейку для хранения вещей.' \
               'Давайте посмотрим адреса складов, чтобы выбрать ближайший!'
        update.message.reply_text(text)
        time.sleep(1)
        reply_text = 'Выберите склад, для хранения вещей.'
        update.message.reply_text(reply_text, reply_markup=address)
        time.sleep(0.2)
        return STORAGE
    else:
        text = f'Привет, {user_name}.🤚\n\n' \
               'Вы можете арендовать ячейку, либо посмотреть уже арендованные.'
        update.message.reply_text(text)
        time.sleep(1)
        reply_text = 'Выберите следующее действие.'
        actual_buttons = is_orders(update)
        update.message.reply_text(reply_text, reply_markup=actual_buttons)
        time.sleep(0.2)
        return SELECTION


def get_selection_old_user(update, context):
    message = update.message
    selection = message.text
    user_id = message.chat_id
    if selection == 'Создать новую ячейку':
        reply_text = 'Выберите склад, для хранения вещей.'
        update.message.reply_text(reply_text, reply_markup=address)
        time.sleep(0.2)
        return STORAGE
    else:
        user_orders = Order.objects.filter(profile__tg_chat_id__contains=user_id)
        orders_info = []
        for order in user_orders:
            orders_info.append(f'Номер заказа {order.order_number}, хранение {order.things} c {order.start_date} по {order.end_date} по адресу {order.storage_address}')
        update.message.reply_text(
            f'Ваши заказы:\n {orders_info}')
        reply_text = 'Для создания новой ячейки нажмите кнопку.'
        update.message.reply_text(reply_text, reply_markup=new_order)
        time.sleep(0.2)


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
        text = 'Выберите желаемую площадь ячейки для хранения\n' \
               'Можно выбрать размер от 1 до 10 м2'
        update.message.reply_text(text, reply_markup=other_things)
        return CELL_SIZE

    if storage_type == 'сезонные вещи':
        reply_text = 'Выберете вещи.'
        update.message.reply_text(reply_text, reply_markup=seasonal_things)
        return THINGS


def select_storage_cell_size(update, context):
    message = update.message
    user_id = message.chat_id
    cell_size = int(message.text)
    if cell_size in range(1, 11):
        price = 599 + 150 * (cell_size - 1)
        storage_info[user_id]['cell_size'] = cell_size
        text = f'Стоимость хранения составит {price} рублей\n' \
               f'Выберите срок хранения'
        update.message.reply_text(
            text,
            reply_markup=tires_storage_period,
        )
        return SELECT_SIZE



def get_other_storage_cell_size(update, context):
    message = update.message
    user_id = message.chat_id
    select = message.text
    if select =='больше месяца, но менее полугода':
        update.message.reply_text('Принято.', reply_markup=more_storage_period)
        return SELECT_CELL_SIZE

    if select == 'больше 6 месяцев, но менее года':
        update.message.reply_text('Принято.', reply_markup=more_6_months_storage_period)
        return SELECT_CELL_SIZE

    else:
        storage_info[user_id]['storage_period'] = select
        update.message.reply_text(
            'Отлично! Теперь вы можете забронировать ячейку.',
            reply_markup=reserve)
        return RESERVE



def get_select_storage_cell_size(update, context):
    message = update.message
    user_id = message.chat_id
    select = message.text
    if select=='назад':
        text='Принято.'
        update.message.reply_text(
            text,
            reply_markup=tires_storage_period,
        )
        print('принято')
        return SELECT_SIZE
    else:
        storage_info[user_id]['storage_period'] = select
        update.message.reply_text(
            'Отлично! Теперь вы можете забронировать ячейку.',
            reply_markup=reserve)
        return RESERVE


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
    number_things = message.text
    if number_things.isdigit() and int(number_things) < 100:
        storage_info[user_id]['number_things'] = number_things
        time.sleep(0.3)
        things = storage_info[user_id].get('things')
        price_per_week = Stuff.objects.get(stuff_name=things).price_per_week
        price_per_month = Stuff.objects.get(stuff_name=things).price_per_month
        if things in ('лыжи', 'сноуборд', 'велосипед'):
            reply_text = f'Выберете срок хранения {things}.\n Стоимость хранения {number_things} ед. в неделю {price_per_week*int(number_things)}, в месяц {price_per_month*int(number_things)}.'
            update.message.reply_text(reply_text, reply_markup=storage_period)
            return PERIOD
        if things == 'колеса':
            reply_text = f'Выберете срок хранения {things}.\n Стоимость хранения {number_things} ед. в месяц {price_per_month*int(number_things)}.'
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
    if storage_period == 'больше месяца, но менее полугода':
        update.message.reply_text('Принято.', reply_markup=more_storage_period)
        return CHECK_PERIOD
    if storage_period == 'меньше месяца, но больше недели':
        update.message.reply_text('Принято.', reply_markup=less_month_storage_period)
        return CHECK_PERIOD

    else:
        storage_info[user_id]['storage_period'] = storage_period
        update.message.reply_text(
            'Отлично! Теперь вы можете забронировать ячейку.',
            reply_markup=reserve)
        return RESERVE


def reserve_cell(update, context):
    message = update.message
    storage_period = message.text

    if storage_period == 'Зарезервировать':
        user_info = get_user_data_from_db(update)
        if not user_info:
            update.message.reply_text(
                'Пожалуйста, введите ваше ФИО, например - Иванов Иван Иванович',
            )
            return INITIALS
        else:
            update.message.reply_text(
                f'Отлично! Теперь можно приступить к оплате.',
                reply_markup=byu_or_menu
            )
        return CHECKOUT
    else:
        return start(update, context)


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
        update.message.reply_text(
            'Отлично! Теперь вы можете забронировать ячейку.',
            reply_markup=reserve)
        return RESERVE


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
            'Пожалуйста, введите ваши паспортные данные в формаете СЕРИЯ НОМЕР\n'
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

def save_user_to_db(update, context):
    message = update.message
    user_id = message.chat_id
    user, _ = Profile.objects.get_or_create(tg_chat_id=user_id)
    user.full_name = storage_info[user_id].get('fio')
    user.tg_chat_id = user_id
    user.phone = storage_info[user_id].get('phone')
    user.passport_date = storage_info[user_id].get('passport')
    user.birthdate =  storage_info[user_id].get('birth_date')
    user.save()


def create_order(update, context):
    message = update.message
    birth_date = message.text
    user_id = message.chat_id
    storage_type = storage_info[user_id]['storage_type']
    address = storage_info[user_id]['address']
    period = storage_info[user_id]['storage_period']
    fio = storage_info[message.chat_id]['fio']
    passport = storage_info[message.chat_id]['passport']
    phone = storage_info[message.chat_id]['phone']
    things = storage_info[user_id].get('things')
    if is_valid_birth_date(birth_date):
        storage_info[user_id]['birth_date'] = birth_date
        if not things:
            things = ''
        update.message.reply_text(
            f'Отлично! Мы получили от вас следующие данные:\nФИО: {fio}\nПаспортные данные: {passport}\nТелефон: {phone}\nАдрес хранения: {address}\nТип хранения: {storage_type}\nВещь: {things}\nПериод хранения: {period}',
            reply_markup=byu_or_menu
        )
        return CHECKOUT
    else:
        update.message.reply_text(
            'Дата рождения введена некорректно, нужный формат - ГОД-МЕСЯЦ-ЧИСЛО\n'
            'Например: 1991-08-17',
        )
def get_things_price(period, number_things, things_weekly_price, things_monthly_price):
    amount, interval = period.split()
    if interval.startswith('н'):
        all_price = int(amount) * int(number_things) * int(things_weekly_price)
        return all_price
    else:
        all_price = int(amount) * int(number_things) * int(things_monthly_price)
        return all_price

def save_order_to_db(update, context, qr_code_path, time_from, time_to, all_price):
    message = update.message
    user_id = message.chat_id
    address = storage_info[user_id]['address']
    things = storage_info[user_id].get('things')
    try:
        order_number = Order.objects.latest('order_number').order_number + 1
    except Order.DoesNotExist:
        order_number = 1
    if things:
        order = Order.objects.create(
            order_number=order_number,
            profile = Profile.objects.get(tg_chat_id=user_id),
            order_price=all_price,
            start_date = time_from,
            end_date = time_to,
            things = things,
            storage_address =  address,
            qr_code = qr_code_path,
        )
        order.save
    else:
        order = Order.objects.create(
            order_number=order_number,
            profile=Profile.objects.get(tg_chat_id=user_id),
            order_price=1000,
            start_date=time_from,
            end_date=time_to,
            storage_address=address,
            qr_code=qr_code_path,
        )
        order.save

def checkout(update, context):
    message = update.message
    choice = message.text
    user_id = message.chat_id
    if choice == 'Оплатить':
        storage_period = storage_info[user_id]['storage_period']
        address = storage_info[user_id].get('address')
        number_things = storage_info[user_id].get('number_things')
        things = storage_info[user_id].get('things')
        period = storage_info[user_id].get('storage_period')
        if things:
            things_weekly_price = Stuff.objects.get(stuff_name=things).price_per_week
            things_monthly_price = Stuff.objects.get(stuff_name=things).price_per_month
            all_price = get_things_price(period, number_things, things_weekly_price, things_monthly_price)
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
        period = storage_info[message.chat_id]['storage_period']
        time_from = datetime.now()
        time_to = time_from + get_storage_interval_timedelta(period)
        if get_user_data_from_db(update):
            save_order_to_db(update, context, qr_code_path, time_from, time_to, all_price)
        else:
            save_user_to_db(update, context)
            save_order_to_db(update, context, qr_code_path, time_from, time_to, all_price)
        update.message.reply_text(
            'Вот ваш электронный ключ для доступа к вашему личному складу.'
            f'Вы сможете попасть на склад в любое время в период с {time_from.date()} по {time_to.date()}',
        )
        text='Для выхода в меню нажмите кнопку.'
        update.message.reply_text(text, reply_markup=menu)
        return MENU
    else:
        return start(update, context)

def get_menu(update, context):
    message = update.message
    menu = message.text
    if menu =='Главное меню':
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

                SELECTION: [CommandHandler('start', start),
                            MessageHandler(Filters.text,
                                           get_selection_old_user)],

                STORAGE: [CommandHandler('start', start),
                          MessageHandler(Filters.text, get_storage)],

                CATEGORY: [CommandHandler('start', start),
                           MessageHandler(Filters.text, choose_category)],

                CELL_SIZE: [CommandHandler('start', start),
                            MessageHandler(Filters.text,
                                           select_storage_cell_size)],

                SELECT_SIZE: [CommandHandler('start', start),
                              MessageHandler(Filters.text,
                                             get_other_storage_cell_size)],
                SELECT_CELL_SIZE: [CommandHandler('start', start),
                              MessageHandler(Filters.text,
                                             get_select_storage_cell_size)],

                THINGS: [CommandHandler('start', start),
                         MessageHandler(Filters.text, get_things)],

                QUANTITY: [CommandHandler('start', start),
                           MessageHandler(Filters.text, get_quantity)],

                PERIOD: [CommandHandler('start', start),
                         MessageHandler(Filters.text, get_storage_period)],

                CHECK_PERIOD: [CommandHandler('start', start),
                               MessageHandler(Filters.text,
                                              check_storage_period)],
                RESERVE: [CommandHandler('start', start),
                          MessageHandler(Filters.text,
                                         reserve_cell)],

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
                MENU: [CommandHandler('start', start),
                           MessageHandler(Filters.text,
                                          get_menu)],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()