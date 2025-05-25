from meetapp.models import User

from .scene_router import SceneRouter


class SubscriptionScene:
    def handle(self, update, context):
        scene = SceneRouter.get('main_menu')
        context.user_data['scene'] = self

        tg_id = update.effective_user.id
        user = User.objects.filter(tg_id=tg_id).first()

        message = update.message or update.callback_query.message

        if user:
            if user.is_subscribed:
                message.reply_text("🔔 Вы уже подписаны на уведомления о будущих мероприятиях.")
            else:
                user.is_subscribed = True
                user.save()
                message.reply_text("✅ Вы подписались на уведомления о будущих мероприятиях!")
        else:
            message.reply_text("⚠️ Вы не зарегистрированы как пользователь. Нажмите /start, чтобы начать.")

        scene.handle(update, context)
