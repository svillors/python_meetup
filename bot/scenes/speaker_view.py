from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils import timezone
from meetapp.models import Question, User

from .scene_router import SceneRouter


class SpeakerQuestionViewerScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        scene = SceneRouter.get('main_menu')
        now = timezone.localtime().time()
        today = timezone.localdate()
        user = User.objects.get(tg_id=update.effective_user.id)
        speaker = user.speaker_profile
        questions = Question.objects.filter(
            event__speaker=speaker,
            event__meetup__date=today,
            event__time_start__lte=now,
            event__time_end__gte=now
        )
        message = update.message or update.callback_query.message
        if not questions:
            message.reply_text('❓ Пока что нет вопросов от участников.')
            scene.handle(update, context)
        else:
            context.user_data['stage'] = 'watch_questions'
            cancel_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('⏪ Назад', callback_data='back_to_menu')]
            ])
            message.reply_text(
                build_questions_list(questions),
                parse_mode='Markdown',
                reply_markup=cancel_markup
            )

    def process_callback(self, update, context):
        query = update.callback_query
        stage = context.user_data.get('stage')
        scene = SceneRouter.get('main_menu')
        if stage == 'watch_questions':
            if query.data == 'back_to_menu':
                query.answer()
                query.message.delete()
                scene.handle(update, context)


def build_questions_list(questions):
    lines = ["📬 *Вопросы от слушателей:*", ""]
    for i, q in enumerate(questions, start=1):
        time_str = q.time.strftime('%H:%M')
        asker_name = q.asker.first_name or "Аноним"
        text = q.text.strip()

        lines.append(
            f"*{i}. {asker_name}* в {time_str}:\n{text}\n"
        )

    return "\n".join(lines)
