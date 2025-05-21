from scenes.main_menu import MainMenuScene


class AskQuestionScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        context.user_data['stage'] = 'awaiting_question'
        update.message.reply_text('Сейчас выступает спикер. Напишите ваш вопрос:')

    def process(self, update, context):
        if context.user_data.get('stage') == 'awaiting_question':
            question = update.message.text
            context.user_data['last_question'] = question
            update.message.reply_text('✅ Вопрос отправлен. Спасибо!')
            MainMenuScene().handle(update, context)
