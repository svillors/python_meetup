from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from meetapp.models import Application, User

from .scene_router import SceneRouter


class CreateApplicationScene:

    def handle(self, update, context):
        context.user_data['scene'] = self
        message = update.message or update.callback_query.message
        cancel_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ Отмена', callback_data='decline_application')]
        ])
        context.user_data['stage'] = 'awaiting_application'
        message.reply_text(
            'Напишите о том, что бы вы хотели провести:',
            reply_markup=cancel_markup
        )

    def process(self, update, context):
        stage = context.user_data.get('stage')
        if stage == 'awaiting_application':
            application = update.message.text
            context.user_data['application'] = application
            context.user_data['stage'] = 'approve_application'
            keyboard = [
                [InlineKeyboardButton(
                    '✉️ Отправить',
                    callback_data='confirm_application'
                )],
                [InlineKeyboardButton(
                    '✍️ Изменить',
                    callback_data='decline_application'
                )]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                'Отправить заявку?',
                reply_markup=markup
            )

    def process_callback(self, update, context):
        query = update.callback_query
        stage = context.user_data.get('stage')
        scene = SceneRouter.get('main_menu')
        if stage == 'awaiting_application':
            if query.data == 'decline_application':
                query.answer()
                query.message.delete()
                scene.handle(update, context)
        if stage == 'approve_application':
            if query.data == 'confirm_application':
                text = context.user_data.get('application')
                user_id = update.effective_user.id
                user = User.objects.get(tg_id=user_id)
                Application.objects.create(
                    text=text,
                    applicant=user
                )
                query.answer(
                    text="💡 Заявка успешно отправлена!",
                    show_alert=True
                )
                query.message.delete()
                scene.handle(update, context)
            elif query.data == 'decline_application':
                query.answer()
                context.user_data['stage'] = 'awaiting_application'
                query.message.delete()
                self.handle(update, context)
