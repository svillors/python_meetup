import os
import django
import time
from datetime import datetime, timedelta
from django.utils import timezone

from dotenv import load_dotenv
from telegram import Bot

from django.utils.timezone import make_aware
from datetime import timezone as dt_timezone
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "python_meetup.settings")
django.setup()

from meetapp.models import Meetup, User

load_dotenv()
bot = Bot(token=os.getenv("TG_BOT_TOKEN"))


def send_meetup_notifications():
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)
    upcoming_window_start = now + timedelta(minutes=1)
    upcoming_window_end = now + timedelta(minutes=3)

    meetups = Meetup.objects.all()

    for meetup in meetups:
        naive_dt = datetime.combine(meetup.date, meetup.start_meetup)
        meetup_dt = moscow_tz.localize(naive_dt)

        if upcoming_window_start <= meetup_dt < upcoming_window_end:
            text = (
                f"🔔 Скоро начнётся мероприятие: {meetup.title}\n"
                f"📍 Место: {meetup.location}\n"
                f"🕒 Время: {meetup.start_meetup.strftime('%H:%M')}"
            )

            subscribers = User.objects.filter(is_subscribed=True)
            for user in subscribers:
                try:
                    bot.send_message(chat_id=user.tg_id, text=text)
                except Exception as e:
                    print(f"Не удалось отправить сообщение {user.username}: {e}")


if __name__ == "__main__":
    while True:
        send_meetup_notifications()
        time.sleep(60)
