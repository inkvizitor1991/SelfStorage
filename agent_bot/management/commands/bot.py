import logging
import time
import telegram

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

STORAGE, CATEGORY, THINGS, QUANTITY, PERIOD, CHECK_PERIOD, INITIALS = range(7)

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


def start(update, context):
    time.sleep(0.5)
    user = update.message.from_user
    text = f'Привет {user.first_name}! \nSelfStorage, аренда складов в г.Санкт-Петербург.'
    update.message.reply_text(text)
    chat_id = update.message.chat_id
    context.user_data['user_id'] = update.message.chat_id
    context.user_data['first_name'] = update.message.from_user.first_name
    context.user_data['last_name'] = update.message.from_user.last_name
    context.user_data['username'] = update.message.from_user.username

    chat_id = update.message.chat_id
    first_name = context.user_data.get('first_name')
    last_name = context.user_data.get('last_name')
    username = context.user_data.get('username')
    time.sleep(1)
    reply_text = 'Выберите склад, для хранения вещей.'
    update.message.reply_text(reply_text, reply_markup=address)
    time.sleep(0.2)
    return STORAGE
    # profile, _ = Profile.objects.get_or_create( ### сохраняет в бд, она нужна в конце кода
    #    external_id=chat_id,
    #    defaults={
    #        'name': username,
    #        'first_name': first_name,
    #        'last_name': last_name,
    #    }
    # )#


#
# Order(
#    profile=profile,
# ).save()

def get_storage(update, context):
    user_message = update.message.text
    context.user_data['storage'] = user_message
    if user_message == 'Пироговская набережная 15 (м.Площадь Ленина)':
        print(user_message)
    reply_text = 'Что хотите хранить?'
    update.message.reply_text(reply_text, reply_markup=choosing_category)
    time.sleep(0.2)
    return CATEGORY


def choose_category(update, context):
    user_message = update.message.text
    print(user_message)
    if user_message == 'другое':
        print('ок')
    if user_message == 'сезонные вещи':
        reply_text = 'Выберете вещи.'
        update.message.reply_text(reply_text, reply_markup=seasonal_things)
        return THINGS


def get_things(update, context):
    user_message = update.message.text
    context.user_data['things'] = user_message
    if user_message:
        update.message.reply_text('Укажите кол-во.')
        return QUANTITY


def get_quantity(update, context):
    user_message = update.message.text
    print(user_message)
    if user_message.isdigit() and int(user_message) < 100:
        context.user_data['quantity'] = user_message
        update.message.reply_text('Стоимость: 10000 за месяц')
        print('Тут пользователю отправляется стоимость хранения вещи.')
        time.sleep(0.3)
        things = context.user_data.get('things')
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
    user_message = update.message.text
    print(user_message)
    if user_message == 'больше месяца но меньше пол года':
        update.message.reply_text('Принято.', reply_markup=more_storage_period)
        return CHECK_PERIOD
    else:
        context.user_data['storage_period'] = user_message
        print(user_message)
        update.message.reply_text('Принято.')
        update.message.reply_text('Напишите ФИО.')
        return INITIALS


def check_storage_period(update, context):
    user_message = update.message.text
    things = context.user_data.get('things')
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
        context.user_data['storage_period'] = user_message
        print(user_message)
        update.message.reply_text('Принято.')
        update.message.reply_text('Напишите ФИО.')
        return INITIALS


def get_initials(update, context):
    user_message = update.message.text
    print(user_message)
    print('we here')
    update.message.reply_text('Хорошо!Теперь укажите кредитную карту!')


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
            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
