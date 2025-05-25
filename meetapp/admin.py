from django.contrib import admin
from meetapp.models import User, Speaker, Event, Meetup, Question, Application


class SpeakerInline(admin.StackedInline):
    model = Speaker
    extra = 0
    max_num = 1
    verbose_name = 'Профиль спикера'


class EventInline(admin.StackedInline):
    model = Event
    extra = 0
    verbose_name = 'Событие меропритя'
    verbose_name_plural = 'События мероприятия'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'role', 'tg_id']
    search_fields = ['first_name', 'tg_id']
    ordering = ['-role']
    inlines = [SpeakerInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance

        has_profile = Speaker.objects.filter(user=user).exists()
        new_role = 'speaker' if has_profile else 'listener'

        if user.role != new_role:
            user.role = new_role
            user.save(update_fields=['role'])


@admin.register(Meetup)
class MeetupAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']
    ordering = ['-date']
    inlines = [EventInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['asker', 'event', 'time']
    ordering = ['-time']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'text']
