from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils import timezone
from meetapp.models import Question, Event, User

from .scene_router import SceneRouter


class AskQuestionScene:
    def __init__(self):
        now = timezone.localtime()
        self.event = Event.objects.filter(
            meetup__date=now.date(),
            time_start__lte=now.time(),
            time_end__gte=now.time()
        ).first()

    def handle(self, update, context):
        context.user_data['scene'] = self
        scene = SceneRouter.get('main_menu')
        message = update.message or update.callback_query.message
        if not self.event:
            message.reply_text('🫥 Сейчас ничего не проводится')
            scene.handle(update, context)
        elif not self.event.speaker:
            message.reply_text('🤐 Сейчас никто не выступает')
            scene.handle(update, context)
        else:
            cancel_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('❌ Отмена', callback_data='decline_question')]
            ])
            context.user_data['stage'] = 'awaiting_question'
            message.reply_text(
                f'🎤 Сейчас выступает {self.event.speaker.name}\n✍️ Напишите ваш вопрос:',
                reply_markup=cancel_markup
            )

    def process(self, update, context):
        stage = context.user_data.get('stage')
        if stage == 'awaiting_question':
            question = update.message.text
            context.user_data['question'] = question
            context.user_data['stage'] = 'approve_question'
            keyboard = [
                [InlineKeyboardButton(
                    '✉️ Отправить',
                    callback_data='confirm_question'
                )],
                [InlineKeyboardButton(
                    '✍️ Изменить',
                    callback_data='decline_question'
                )]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                '🎤 Отправить этот вопрос докладчиу?',
                reply_markup=markup
            )

    def process_callback(self, update, context):
        query = update.callback_query
        stage = context.user_data.get('stage')
        scene = SceneRouter.get('main_menu')
        if stage == 'awaiting_question':
            if query.data == 'decline_question':
                query.answer()
                query.message.delete()
                scene.handle(update, context)
        if stage == 'approve_question':
            if query.data == 'confirm_question':
                text = context.user_data.get('question')
                user_id = update.effective_user.id
                user = User.objects.get(tg_id=user_id)
                Question.objects.create(
                    text=text, event=self.event,
                    asker=user
                )
                query.answer(
                    text="💡 Вопрос усешно отправлен!",
                    show_alert=True
                )
                query.message.delete()
                scene.handle(update, context)
            elif query.data == 'decline_question':
                query.answer()
                context.user_data['stage'] = 'awaiting_question'
                query.message.delete()
                self.handle(update, context)
