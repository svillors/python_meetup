import re
import os
import random

from telegram import LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from .scene_router import SceneRouter


class DonateScene:
    def __init__(self):
        load_dotenv()
        self.provider_token = os.getenv('PROVIDER_TOKEN')

    def handle(self, update, context):
        context.user_data['scene'] = self
        context.user_data['stage'] = 'set_price'

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('200 ₽', callback_data='donate_200')],
            [InlineKeyboardButton('500 ₽', callback_data='donate_500')],
            [InlineKeyboardButton('1000 ₽', callback_data='donate_1000')],
            [InlineKeyboardButton('2000 ₽', callback_data='donate_2000')],
            [InlineKeyboardButton('💬 Ввести свою сумму', callback_data='donate_custom')],
            [InlineKeyboardButton('❌ Отмена', callback_data='donate_cancel')]
        ])
        message = update.message or update.callback_query.message
        message.reply_text(
            'Выберите сумму вашего пожертвования',
            reply_markup=markup
        )

    def process(self, update, context):
        text = update.message.text
        stage = context.user_data['stage']

        cancel_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ Отмена', callback_data='decline_payment')]
        ])
        if stage == 'select_amount':
            if re.match(r'^\d+$', text):
                price = int(text)
                update.message.reply_text(
                    "Готовим ссылку для оплаты...",
                    reply_markup=cancel_markup
                )
                create_donate(update, context, price, self.provider_token)
            else:
                update.message.reply_text('Введите только число')

    def process_callback(self, update, context):
        query = update.callback_query
        query.answer()
        stage = context.user_data['stage']
        cancel_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ Отмена', callback_data='decline_payment')]
        ])
        if stage == 'set_price':
            if query.data == 'donate_cancel':
                scene = SceneRouter.get('main_menu')
                query.message.delete()
                scene.handle(update, context)
            elif query.data.startswith('donate_') and query.data != 'donate_custom':
                price = int(query.data.split('_')[1])
                context.user_data['stage'] = 'end_payment'
                query.message.edit_text(
                    "Готовим ссылку для оплаты...",
                    reply_markup=cancel_markup
                )
                create_donate(update, context, price, self.provider_token)
            elif query.data == 'donate_custom':
                context.user_data['stage'] = 'select_amount'
                query.message.edit_text(
                    "Введите желаемую сумму цифрами (например, 500):",
                    reply_markup=cancel_markup
                )

        elif stage == 'select_amount':
            if query.data == 'decline_payment':
                scene = SceneRouter.get('main_menu')
                query.message.delete()
                scene.handle(update, context)

        elif stage == 'end_payment':
            if query.data == 'decline_payment':
                scene = SceneRouter.get('main_menu')
                query.message.delete()
                scene.handle(update, context)


def create_donate(update, context, money_amount, provider_token):
    title = "Поддержка проекта"
    description = "Пожертвование на развития нашего сообщества"
    payload = f"{update.effective_chat.id}" + f'{random.randint(1, 99999)}'
    provider_token = provider_token
    currency = "RUB"
    prices = [
        LabeledPrice(f"Поддержать на {money_amount} ₽", money_amount * 100)
    ]
    context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        start_parameter="donate",
        currency=currency,
        prices=prices,
    )
