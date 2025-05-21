from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


class ConnectionScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        context.user_data['stage'] = 'about_me'
        update.message.reply_text('Для начала напиши о себе.')

    def process(self, update, context):
        text = update.message.text
        stage = context.user_data['stage']

        if stage == 'about_me':
            context.user_data['stage'] = 'confirm_about'

            keyboard = [
                [InlineKeyboardButton('Подтвердить', callback_data='confirm_about')],
                [InlineKeyboardButton('Изменить', callback_data='decline_about')]
            ]
            markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                'Сохранить ли анкету?',
                reply_markup=markup
            )

    def process_callback(self, update, context):
        query = update.callback_query

        if query.data == 'confirm_about':
            context.user_data['stage'] = 'random_person'
            query.answer()
            query.message.reply_text('Отлично! Начинайте общение!')

        elif query.data == 'decline_about':
            context.user_data['stage'] = 'about_me'
            query.answer()
            query.message.reply_text('Заполните анкету заново')
