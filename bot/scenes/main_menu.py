from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from meetapp.models import User

from .scene_router import SceneRouter


class MainMenuScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        keyboard = [
            [
                InlineKeyboardButton(
                    '🗓 Расписание мероприятия',
                    callback_data='schedule'
                ),
                InlineKeyboardButton(
                    '🤝 Знакомства',
                    callback_data='network'
                )
            ],
            [
                InlineKeyboardButton(
                    '❓ Задать вопрос спикеру',
                    callback_data='ask'
                ),
                InlineKeyboardButton(
                    '💸 Поддержать организаторов',
                    callback_data='donate'
                )
            ],
            [
                InlineKeyboardButton(
                    'Стать спикером',
                    callback_data='application'
                )
            ]
        ]
        user_id = update.effective_user.id
        user = User.objects.filter(tg_id=user_id).first()

        is_speaker = User.objects.filter(tg_id=user_id, role='speaker').exists()
        if is_speaker:
            keyboard.append([InlineKeyboardButton(
                '👀 Посмотреть вопросы',
                callback_data='show_questions'
            )])

        if user and user.is_subscribed:
            keyboard.append([InlineKeyboardButton(
                '🚫 Отписаться от рассылки', 
                callback_data='unsubscribe'
            )])
        elif user:
            keyboard.append([InlineKeyboardButton(
                '🔔 Подписаться на мероприятия', 
                callback_data='subscribe'
            )])

        if user.is_admin:
            keyboard.append([InlineKeyboardButton(
                '📢 Сделать рассылку', 
                callback_data='broadcast'
            )])

        markup = InlineKeyboardMarkup(keyboard)
        message = update.message or update.callback_query.message
        message.reply_text(
            '🎮 Меню бота',
            reply_markup=markup
        )

    def process_callback(self, update, context):
        query = update.callback_query
        query.answer()

        if query.data == 'schedule':
            scene = SceneRouter.get('schedule')
            query.answer()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'network':
            scene = SceneRouter.get('connection')
            query.answer()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'ask':
            scene = SceneRouter.get('ask_question')
            query.answer()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'donate':
            scene = SceneRouter.get('donate')
            query.answer()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'show_questions':
            scene = SceneRouter.get('speaker_view')
            query.answer()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'subscribe':
            from .subscription import SubscriptionScene
            scene = SubscriptionScene()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'broadcast':
            from .broadcast import BroadcastScene
            scene = BroadcastScene()
            query.message.delete()
            scene.handle(update, context)

        if query.data == 'unsubscribe':
            from .unsubscribe import UnsubscribeScene
            scene = UnsubscribeScene()

        if query.data == 'application':
            scene = SceneRouter.get('create_application')
            query.answer()
            query.message.delete()
            scene.handle(update, context)
