from telegram import ReplyKeyboardMarkup

from .scene_router import SceneRouter


from .connection import ConnectionScene
from .schedule import ScheduleScene
from .ask_question import AskQuestionScene
from .speaker_view import SpeakerQuestionViewerScene


SPEAKER_IDS = []


class MainMenuScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        keyboard = [
            ['Расписание мероприятия'],
            ['Знакомства'],
            ['Задать вопрос спикеру'],
            ['Поддержать организаторов']
        ]

        if update.effective_user.id in SPEAKER_IDS:
            keyboard.append(['Посмотреть вопросы'])

        markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )

        update.message.reply_text('Выбирай', reply_markup=markup)



    def process(self, update, context):
        text = update.message.text

        if text == 'Расписание мероприятия':
            scene = SceneRouter.get('schedule')
            scene.handle(update, context)

        elif text == 'Знакомства':
            scene = SceneRouter.get('connection')
            scene.handle(update, context)

        elif text == 'Задать вопрос спикеру':
            scene = SceneRouter.get('ask_question')
            scene.handle(update, context)

        elif text == 'Поддержать организаторов':
            scene = SceneRouter.get('donate')
            scene.handle(update, context)

        elif text == 'Посмотреть вопросы':
            from .speaker_view import SpeakerQuestionViewerScene
            scene = SpeakerQuestionViewerScene()
            scene.handle(update, context)
