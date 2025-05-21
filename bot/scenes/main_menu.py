from telegram import ReplyKeyboardMarkup

from .scene_router import SceneRouter


class MainMenuScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        keyboard = [
            ['Расписание мероприятия'],
            ['Знакомства'],
            ['Задать вопрос спикеру'],
            ['Поддержать организаторов']
        ]
        markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        update.message.reply_text('Выбирай', reply_markup=markup)

    def process(self, update, context):
        text = update.message.text

        if text == 'Расписание мероприятия':
            update.message.reply_text('вот расписание')

        elif text == 'Знакомства':
            scene = SceneRouter.get('connection')
            scene.handle(update, context)

        elif text == 'Задать вопрос спикеру':
            scene = None
            scene.handle(update, context)

        elif text == 'Поддержать организаторов':
            scene = SceneRouter.get('donate')
            scene.handle(update, context)
