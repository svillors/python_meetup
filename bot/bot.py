import os

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    PreCheckoutQueryHandler
)
from dotenv import load_dotenv

from utils.init_django import init_django
init_django()

from meetapp.models import User

from scenes.scene_router import SceneRouter
from scenes.connection import ConnectionScene
from scenes.donate import DonateScene
from scenes.main_menu import MainMenuScene
from scenes.ask_question import AskQuestionScene
from scenes.schedule import ScheduleScene


SceneRouter.scenes = {
    'main_menu': MainMenuScene,
    'connection': ConnectionScene,
    'donate': DonateScene,
    'ask_question': AskQuestionScene,
    'schedule': ScheduleScene
}


def start(update, context):
    tg_user = update.effective_user
    speaker_ids = context.bot_data.get('SPEAKER_IDS', [])

    if tg_user.username:
        role = 'speaker' if tg_user.id in speaker_ids else 'listener'
        User.objects.get_or_create(
            tg_id=tg_user.id,
            defaults={
                'first_name': tg_user.first_name or '',
                'username': tg_user.username,
                'role': role,
            }
        )

    update.message.reply_text('я бот, бизнес митапы бизнес деньги')
    scene = SceneRouter.get('main_menu')
    scene.handle(update, context)



def universal_handler(update, context):
    scene = context.user_data.get('scene')
    if not scene:
        update.callback_query.answer('что-то сломалось, чини')
    scene.process(update, context)


def callback_handler(update, context):
    scene = context.user_data.get('scene')
    if not scene:
        if update.callback_query:
            update.callback_query.answer('что-то сломалось, чини')
        elif update.message:
            update.message.reply_text('что-то сломалось, чини')
        return
    scene.process_callback(update, context)


def precheckout_handler(update, context):
    query = update.pre_checkout_query
    query.answer(ok=True)


def payment_success(update, context):
    update.message.reply_text('Спасибо за поддержку!')


def main():
    load_dotenv()
    
    SPEAKER_IDS = list(map(int, os.getenv("SPEAKER_IDS", "").split(",")))

    updater = Updater(os.getenv('TG_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data['SPEAKER_IDS'] = SPEAKER_IDS

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, universal_handler))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment, payment_success))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
