import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from dotenv import load_dotenv

from scenes.main_menu import MainMenuScene


def start(update, context):
    update.message.reply_text('я бот, бизнес митапы бизнес деньги')
    scene = MainMenuScene()
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


def main():
    load_dotenv()
    updater = Updater(os.getenv('TG_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, universal_handler))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
