from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from meetapp.models import Meetup
from django.utils import timezone

from .scene_router import SceneRouter


class ScheduleScene:
    def handle(self, update, context):
        context.user_data['scene'] = self
        context.user_data['stage'] = 'choose_schedule'

        schedule_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                '🎤 Расписание текущего мероприятия',
                callback_data='schedule_today'
            )],
            [InlineKeyboardButton(
                '📆 Предстоящие мероприятия',
                callback_data='schedule_future'
            )]
        ])
        message = update.message or update.callback_query.message
        message.reply_text(
            'Выберите, что хотите узнать:',
            reply_markup=schedule_markup
        )

    def process_callback(self, update, context):
        query = update.callback_query
        scene = SceneRouter.get('main_menu')
        if query.data == 'schedule_today':
            today = timezone.localdate()
            meetup_today = Meetup.objects.filter(date=today).first()
            if not meetup_today:
                query.answer()
                query.message.reply_text(
                    'На сегодня мероприятий не назначено'
                )
                scene.handle(update, context)
            else:
                query.answer()
                query.message.reply_text(
                    build_meetup_schedule(meetup_today),
                    parse_mode='Markdown'
                )
                query.message.delete()
                scene.handle(update, context)
        if query.data == 'schedule_future':
            query.answer()
            query.message.delete()
            today = timezone.localdate()
            meetups = (
                Meetup.objects
                .filter(date__gte=today)
                .order_by('date', 'start_meetup')
            )[:5]
            if not meetups:
                query.message.reply_text(
                    'Пока мероприятий не запланировано'
                )
                scene.handle(update, context)
            else:
                query.message.reply_text(
                    build_future_meetup_schedule(meetups),
                    parse_mode='Markdown'
                )
                scene.handle(update, context)


def build_meetup_schedule(meetup):
    header = (
        f"*🎤 {meetup.title}*\n"
        f"🗓 Дата: *{meetup.date.strftime('%d.%m.%y')}*\n"
        f"🕒 Время: `{meetup.start_meetup.strftime('%H:%M')} – {meetup.end_meetup.strftime('%H:%M')}`\n"
        f"📍 Место: _{meetup.location}_\n\n"
        f"*Программа выступлений:*\n"
    )

    lines = []
    events = meetup.events.order_by('time_start')
    for ev in events:
        start = ev.time_start.strftime('%H:%M')
        end = ev.time_end.strftime('%H:%M')
        title = f"*{ev.title}*"
        speaker = f"\n👤 _{ev.speaker.name}_" if ev.speaker else ""

        block = f"• {title}\n  🕒 {start} – {end}{speaker}"
        lines.append(block)

    return header + "\n\n".join(lines)


def build_future_meetup_schedule(meetups):
    if not meetups:
        return "😕 Пока не запланировано ни одного мероприятия."

    header = "📆 *Ближайшие мероприятия:*\n\n"
    lines = []

    for meetup in meetups:
        date_str = meetup.date.strftime('%d.%m.%y')
        time_str = f"{meetup.start_meetup.strftime('%H:%M')} – {meetup.end_meetup.strftime('%H:%M')}"
        line = (
            f"🗓 *{date_str}* — *{meetup.title}*\n"
            f"🕐 Время: `{time_str}`\n"
            f"📍 Место: _{meetup.location}_\n"
        )
        lines.append(line)

    return header + "\n\n".join(lines)
