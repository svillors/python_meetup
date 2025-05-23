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
            ]
        ]
        user_id = update.effective_user.id
        is_speaker = User.objects.filter(tg_id=user_id, role='speaker').exists()
        if is_speaker:
            keyboard.append([InlineKeyboardButton(
                '👀 Посмотреть вопросы',
                callback_data='show_questions'
            )])
        markup = InlineKeyboardMarkup(keyboard)
        message = update.message or update.callback_query.message
        message.reply_text(
            '🎮 Меню бота',
            reply_markup=markup
        )

    def process_callback(self, update, context):
        query = update.callback_query
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
