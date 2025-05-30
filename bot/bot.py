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
from django.db import transaction

from utils.init_django import init_django
init_django()

from meetapp.models import User, DonationMessage

from scenes.scene_router import SceneRouter
from scenes.connection import ConnectionScene
from scenes.donate import DonateScene
from scenes.main_menu import MainMenuScene
from scenes.ask_question import AskQuestionScene
from scenes.schedule import ScheduleScene
from scenes.speaker_view import SpeakerQuestionViewerScene
from scenes.create_application import CreateApplicationScene
from scenes.subscription import SubscriptionScene
from scenes.unsubscribe import UnsubscribeScene
from scenes.broadcast import BroadcastScene


SceneRouter.scenes = {
    'main_menu': MainMenuScene,
    'connection': ConnectionScene,
    'donate': DonateScene,
    'ask_question': AskQuestionScene,
    'schedule': ScheduleScene,
    'speaker_view': SpeakerQuestionViewerScene,
    'create_application': CreateApplicationScene,
    'subscribe': SubscriptionScene,
    'unsubscribe': UnsubscribeScene,
    'broadcast': BroadcastScene
}


def start(update, context):
    tg_user = update.effective_user
    user_exists = User.objects.filter(tg_id=tg_user).exists()

    if not user_exists:
        defaults = {
            'first_name': tg_user.first_name or '',
            'role': 'listener',
        }

        if tg_user.username:
            defaults['username'] = tg_user.username

        User.objects.get_or_create(
            tg_id=tg_user.id,
            defaults=defaults
        )

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

🔈 Стать спикером
  • Нажав на эту кнопку,ты можешь оставить заявку, чтобы самому стать спикером.

  • Только напиши немного информации о себе, и своих талантах, и организаторы свяжутся с тобой!
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
    sp = update.message.successful_payment
    user = User.objects.filter(tg_id=update.effective_user.id).first()
    if not user:
        update.message.reply_text('Спасибо! (но вас нет в БД 🤷‍♂️)')
        return

    amount_rub = sp.total_amount / 100
    with transaction.atomic():
        DonationMessage.objects.create(user=user, amount=amount_rub)

    update.message.reply_text(f'🙏 Спасибо за поддержку: {amount_rub:.2f} ₽')
    update.message.reply_text('Спасибо за поддержку!')


def main():
    load_dotenv()

    SPEAKER_IDS = (
        User.objects
        .filter(role='listener')
        .values_list('tg_id', flat=True)
    )

    updater = Updater(os.getenv('TG_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data['SPEAKER_IDS'] = SPEAKER_IDS

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
