from telegram import ReplyKeyboardMarkup


from .connection import ConnectionScene
from .schedule import ScheduleScene
from .ask_question import AskQuestionScene
class MainMenuScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        keyboard = [
            ['Расписание мероприятия'],
            ['Знакомства'],
            ['Задать вопрос спикеру']
        ]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text('Выбирай', reply_markup=markup)

    def process(self, update, context):
        text = update.message.text

        if text == 'Расписание мероприятия':
            scene = ScheduleScene()
            scene.handle(update, context)

        elif text == 'Знакомства':
            scene = ConnectionScene()
            scene.handle(update, context)

        elif text == 'Задать вопрос спикеру':
            scene = AskQuestionScene
            scene.handle(update, context)
