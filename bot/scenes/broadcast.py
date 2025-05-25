from meetapp.models import User

class BroadcastScene:
    def handle(self, update, context):
        from scenes.main_menu import MainMenuScene

        context.user_data['scene'] = self
        message = update.message or update.callback_query.message
        message.reply_text("📢 Введите текст рассылки, который будет отправлен всем подписанным пользователям:")

    def process(self, update, context):
        text = update.message.text
        count = 0

        for user in User.objects.all():
            try:
                context.bot.send_message(chat_id=user.tg_id, text=f"📢 Сообщение от организаторов:\n\n{text}")
                count += 1
            except Exception as e:
                print(f"❌ Не удалось отправить {user.username}: {e}")

        update.message.reply_text(f"✅ Сообщение отправлено {count} пользователям.")
        MainMenuScene().handle(update, context)
