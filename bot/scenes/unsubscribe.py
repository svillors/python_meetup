from meetapp.models import User

from .scene_router import SceneRouter


class UnsubscribeScene:
    def handle(self, update, context):
        scene = SceneRouter.get('main_menu')

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

        scene.handle(update, context)
