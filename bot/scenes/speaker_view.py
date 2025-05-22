from scenes.main_menu import MainMenuScene


class SpeakerQuestionViewerScene:
    def handle(self, update, context):
        context.user_data['scene'] = self

        questions = context.bot_data.get('questions', [])

        if not questions:
            update.message.reply_text('❌ Пока что нет вопросов от участников.')
        else:
            message = "❓ Вопросы от участников:\n\n"
            for idx, q in enumerate(questions, start=1):
                message += f"{idx}) {q}\n"
            update.message.reply_text(message)

        MainMenuScene().handle(update, context)

    def process(self, update, context):
        pass