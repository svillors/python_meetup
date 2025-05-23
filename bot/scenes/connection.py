from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from django.db.models import Q
from meetapp.models import User

from .scene_router import SceneRouter


class ConnectionScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        tg_id = update.effective_user.id
        user = User.objects.get(tg_id=tg_id)
        if user.about_me:
            context.user_data['stage'] = 'random_person'
            self.process(update, context)
        else:
            keyboard_cancel = [
                ['❌ Отмена']
            ]
            cancel_markup = ReplyKeyboardMarkup(keyboard_cancel)
            context.user_data['stage'] = 'about_me'
            message = update.message or update.callback_query.message
            message.reply_text(
                '✍️ Для начала напиши о себе.\n' \
                '👀 Твою анкету будут видеть другие пользователи',
                reply_markup=cancel_markup
            )

    def process(self, update, context):
        stage = context.user_data['stage']
        tg_id = update.effective_user.id
        user = User.objects.get(tg_id=tg_id)
        if stage == 'about_me':
            text = update.message.text
            if text == '❌ Отмена':
                scene = SceneRouter.get('main_menu')
                scene.handle(update, context)
            else:
                context.user_data['stage'] = 'confirm_about'
                context.user_data['about_me_text'] = text
                keyboard = [
                    [InlineKeyboardButton(
                        'Подтвердить',
                        callback_data='confirm_about'
                    )],
                    [InlineKeyboardButton(
                        'Изменить',
                        callback_data='decline_about'
                    )]
                ]
                markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(
                    'Сохранить ли анкету?',
                    reply_markup=markup
                )

        elif stage == 'random_person':
            keyboard = [
                ['⏩ Пропустить'],
                ['⏪ Назад']
            ]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            random_user = (
                User.objects
                .filter(~Q(tg_id=user.tg_id), ~Q(about_me=''))
                .order_by('?')
                .first()
            )
            message = update.message or update.callback_query.message
            if random_user:
                username = (
                    f"@{random_user.username}"
                    if random_user.username
                    else "❌ Никнейм не указан"
                )

                text = (
                    f"🤝 *Вот кто-то интересный:*\n\n"
                    f"{username}\n"
                    f"*Имя:* {random_user.first_name}\n\n"
                    f"*О себе:*\n_{random_user.about_me}_"
                )
                message.reply_text(
                    text,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                context.user_data['stage'] = 'person_found'
            else:
                message.reply_text("Пока нет подходящих людей :(")
                scene = SceneRouter.get('main_menu')
                scene.handle(update, context)

        elif stage == 'person_found':
            text = update.message.text
            if text == '⏩ Пропустить':
                context.user_data['stage'] = 'random_person'
                self.process(update, context)
            elif text == '⏪ Назад':
                scene = SceneRouter.get('main_menu')
                scene.handle(update, context)

    def process_callback(self, update, context):
        query = update.callback_query
        tg_id = update.effective_user.id
        user = User.objects.get(tg_id=tg_id)
        if query.data == 'confirm_about':
            about_me_text = context.user_data.get('about_me_text')
            if about_me_text:
                user.about_me = about_me_text
                user.save()
                context.user_data['stage'] = 'random_person'
                query.answer()
                query.edit_message_reply_markup(reply_markup=None)
                query.message.reply_text('Отлично! Начинайте общение! 🤝')
                self.handle(update, context)
            else:
                context.user_data['stage'] = 'about_me'
                query.answer()
                query.message.reply_text(
                    'Что-то пошло не так. Попробуйте написать анкету снова.'
                )

        elif query.data == 'decline_about':
            context.user_data['stage'] = 'about_me'
            query.answer()
            query.edit_message_reply_markup(reply_markup=None)
            query.message.reply_text('✍️ Заполните анкету заново')
