import re
import os

from telegram import LabeledPrice, ReplyKeyboardMarkup
from dotenv import load_dotenv

from .scene_router import SceneRouter


class DonateScene:
    def __init__(self):
        load_dotenv()
        self.provider_token = os.getenv('PROVIDER_TOKEN')

    def handle(self, update, context):
        context.user_data['scene'] = self
        context.user_data['stage'] = 'set_price'

        keyboard_donate = [
            ['200 ₽'], ['500 ₽'],
            ['1000 ₽'], ['2000 ₽'],
            ['Ввести свою сумму'],
            ['Отмена']
        ]
        markup = ReplyKeyboardMarkup(
            keyboard_donate,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        update.message.reply_text(
            'Выберите сумму вашего пожертвования',
            reply_markup=markup
        )

    def process(self, update, context):
        text = update.message.text
        stage = context.user_data['stage']

        keyboard_cancel = [
            ['Отмена']
        ]
        cancel_markup = ReplyKeyboardMarkup(keyboard_cancel)
        if stage == 'set_price':
            if text == 'Отмена':
                scene = SceneRouter.get('main_menu')
                scene.handle(update, context)
            elif text == 'Ввести свою сумму':
                context.user_data['stage'] = 'select_amount'
                update.message.reply_text(
                    'Введите желаемую сумму',
                    reply_markup=cancel_markup
                )
            elif re.match(r'^\d+\s?₽$', text):
                price = int(re.sub(r'\D', '', text))
                context.user_data['stage'] = 'end_payment'
                update.message.reply_text(
                    "Готовим ссылку для оплаты...",
                    reply_markup=cancel_markup
                )
                create_donate(update, context, price, self.provider_token)
            else:
                update.message.reply_text(
                    "Пожалуйста, выберите сумму с клавиатуры."
                )

        elif stage == 'select_amount':
            if re.match(r'^\d+$', text):
                price = int(text)
                update.message.reply_text(
                    "Готовим ссылку для оплаты...",
                    reply_markup=cancel_markup
                )
                create_donate(update, context, price, self.provider_token)
            elif text == 'Отмена':
                scene = SceneRouter.get('main_menu')
                scene.handle(update, context)
            else:
                update.message.reply_text('Введите только число')

        elif stage == 'end_payment':
            if text == 'Отмена':
                scene = SceneRouter.get('main_menu')
                scene.handle(update, context)


def create_donate(update, context, money_amount, provider_token):
    title = "Поддержка проекта"
    description = "Пожертвование на развития нашего сообщества"
    payload = "donate_payload_001"
    provider_token = provider_token
    currency = "RUB"
    prices = [
        LabeledPrice(f"Поддержать на {money_amount} ₽", money_amount * 100)
    ]
    context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        start_parameter="donate",
        currency=currency,
        prices=prices,
    )
