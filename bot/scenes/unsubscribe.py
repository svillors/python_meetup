from meetapp.models import User

class UnsubscribeScene:
    def handle(self, update, context):
        from scenes.main_menu import MainMenuScene

        context.user_data['scene'] = self
        tg_id = update.effective_user.id
        user = User.objects.filter(tg_id=tg_id).first()

        message = update.message or update.callback_query.message

        if user:
            user.is_subscribed = False
            user.save()
            message.reply_text("🚫 Вы успешно отписались от уведомлений о мероприятиях.")
        else:
            message.reply_text("⚠️ Вы не зарегистрированы.")

        MainMenuScene().handle(update, context)

    def process(self, update, context):
        pass
