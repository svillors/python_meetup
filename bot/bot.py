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
    update.message.reply_text(
        '''
👋 Я Meetup Bot.

• Показываю расписание 📅

• Принимаю вопросы и шлю их докладчику 🔄

• Знакомлю гостей между собой 🤝

• С радостью принимаю донаты 💸

Всё — развиваемся, общаемся, едим пиццу! 🍕

Для более подробной информации напишите /help.
'''
    )
    scene = SceneRouter.get('main_menu')
    scene.handle(update, context)


def help_command(update, context):
    text = '''
Привет — я Meetup Bot!
Вот что я умею, чтобы сделать митапы живыми и полезными:

🗓 Программа в чате

  • Показываю актуальное расписание (спикеры, темы, время) одним кликом.

  • Или же расписание предстоящих мероприятий.

💬 Вопросы без микрофона

  • Гость пишет вопрос в боте → я мгновенно пересылаю его текущему спикеру.

  • Во время выступления спикер открывает Telegram и отвечает, не теряя нить разговора.

🤝 Умный нетворкинг

  • Каждый гость заполняет мини-анкеты: «чем занимаюсь», «ищу/предлагаю».

  • Я подбираю вам случайного человека, а дальше вы решаете сами: писать или нет 🤝.

💸 Поддержка митапа

  • Кнопка «💸 Донат» ведёт на платёжку (любая сумма).

  • Любая сумма помогает двигать наше сообщество вперед!
'''
    update.message.reply_text(text)


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
    updater = Updater(os.getenv('TG_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(MessageHandler(Filters.text, universal_handler))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment, payment_success))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
