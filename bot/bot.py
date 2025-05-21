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

from scenes.scene_router import SceneRouter
from scenes.connection import ConnectionScene
from scenes.donate import DonateScene
from scenes.main_menu import MainMenuScene


SceneRouter.scenes = {
    'main_menu': MainMenuScene,
    'connection': ConnectionScene,
    'donate': DonateScene
}


def start(update, context):
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
        update.message.reply_text('что-то сломалось, чини')
    scene.process_callback(update, context)


def precheckout_handler(update, context):
    query = update.pre_checkout_query
    query.answer(ok=True)


def payment_success(update, context):
    update.message.reply_text('Спасибо за поддержку!')


def main():
    load_dotenv()
    updater = Updater(os.getenv('TG_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

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
