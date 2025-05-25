from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from django.db.models import Q
from django.db import DataError
from django.core.exceptions import ValidationError
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
            cancel_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    '❌ Отмена',
                    callback_data='decline_about'
                )]
            ])
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
            context.user_data['stage'] = 'confirm_about'
            context.user_data['about_me_text'] = text

            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    '✅ Подтвердить',
                    callback_data='confirm_about'
                )],
                [InlineKeyboardButton(
                    '✍️ Изменить',
                    callback_data='decline_about'
                )]
            ])
            update.message.reply_text('Сохранить ли анкету?', reply_markup=markup)

        elif stage == 'random_person':
            nav_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        '⏩ Пропустить',
                        callback_data='skip_person'
                    ),
                    InlineKeyboardButton(
                        '⏪ Назад',
                        callback_data='back_to_menu'
                    )
                ]
            ])

            random_user = (
                User.objects
                .filter(~Q(tg_id=user.tg_id), ~Q(about_me=''))
                .order_by('?')
                .first()
            )
            msg = update.message or update.callback_query.message

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
                msg.reply_text(
                    text,
                    reply_markup=nav_markup, 
                    parse_mode='Markdown'
                )
                context.user_data['stage'] = 'person_found'
            else:
                msg.reply_text("Пока нет подходящих людей :(")
                SceneRouter.get('main_menu').handle(update, context)

    def process_callback(self, update, context):
        query = update.callback_query
        data = query.data
        tg_id = update.effective_user.id
        user = User.objects.get(tg_id=tg_id)
        main = SceneRouter.get('main_menu')

        if data == 'about_cancel':
            query.answer()
            query.message.delete()
            return main.handle(update, context)

        if data == 'confirm_about':
            about = context.user_data.get('about_me_text')
            if about:
                max_len = user._meta.get_field('about_me').max_length
                if len(about) > max_len:
                    query.answer(
                        text=f'Максимум {max_len} символов. Сейчас {len(about)}.',
                        show_alert=True
                    )
                    return
                try:
                    user.about_me = about
                    user.save()
                except (ValidationError, DataError):
                    query.answer(
                        text='Не удалось сохранить анкету 😕\n'
                            'Попробуйте укоротить текст.',
                        show_alert=True
                    )
                    return
                context.user_data['stage'] = 'random_person'
                query.answer()
                query.edit_message_reply_markup(reply_markup=None)
                query.message.reply_text('Отлично! Начинайте общение! 🤝')
                self.process(update, context)
            else:
                context.user_data['stage'] = 'about_me'
                query.answer()
                query.message.reply_text(
                    'Что-то пошло не так. Попробуйте снова.'
                )

        elif data == 'decline_about':
            context.user_data['stage'] = 'about_me'
            query.answer()
            query.edit_message_reply_markup(reply_markup=None)
            query.message.reply_text('✍️ Заполните анкету заново')

        elif data == 'skip_person':
            query.answer()
            query.message.delete()
            context.user_data['stage'] = 'random_person'
            self.process(update, context)

        elif data == 'back_to_menu':
            query.answer()
            query.message.delete()
            main.handle(update, context)
