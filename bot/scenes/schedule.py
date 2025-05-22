class ScheduleScene:
    def handle(self, update, context):
        from scenes.main_menu import MainMenuScene

        context.user_data['scene'] = self
        update.message.reply_text(
            '📅 Расписание:\n\n'
            '10:00 — Открытие\n'
            '10:30 — Первый спикер\n'
            '11:15 — Кофе-брейк\n'
            '12:00 — Второй спикер'
        )
        MainMenuScene().handle(update, context)

    def process(self, update, context):
        pass
