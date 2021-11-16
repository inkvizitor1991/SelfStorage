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

STORAGE = range(1)

TG_TOKEN = settings.BOT_TOKEN

bot = telegram.Bot(token=TG_TOKEN)

keyboard_adress = [
    ['Пироговская набережная 15 (м.Площадь Ленина)'],
    ['Московское шоссе, 25, корп. 1В (м.Звездная)'],
    ['ул. Крыленко, 3Б ( м. Улица Дыбенко )'],
    ['Мурино, Воронцовский б-р, 3 ( м. Девяткино )'],
]
keyboard_first = ReplyKeyboardMarkup(
    keyboard_adress,
    resize_keyboard=True,
    one_time_keyboard=True
)


def start(update, context):
    time.sleep(1)
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
    update.message.reply_text(reply_text, reply_markup=keyboard_first)
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
    if user_message == 'Санкт-Петербург, Пироговская набережная 15 (м.Площадь Ленина)':
        print('ОКЕЙ')


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

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
