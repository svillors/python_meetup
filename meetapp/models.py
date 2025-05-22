from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('speaker', 'Докладчик'),
        ('listener', 'Слушатель')
    ]
    tg_id = models.CharField(
        'Телеграм id',
        max_length=60,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=100
    )
    about_me = models.CharField(
        'Анкета о себе',
        max_length=300,
        blank=True
    )
    role = models.CharField(
        'Роль',
        choices=ROLE_CHOICES,
        default='listener',
        max_length=10
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Пользователь {self.first_name}'


class Speaker(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='speaker_profile',
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=100,
        verbose_name="ФИО",
    )

    description = models.TextField(
        max_length=100,
        verbose_name='Описание',
        blank=True
    )

    class Meta:
        verbose_name = 'Спикер'
        verbose_name_plural = 'Спикеры'

    def __str__(self):
        return self.name


class Meetup(models.Model):

    title = models.CharField(
        max_length=100,
        verbose_name="Название",
    )
    date = models.DateField(
        verbose_name='Дата митапа'
    )
    start_meetup = models.TimeField(
        'Время начала мероприятия'
    )
    end_meetup = models.TimeField(
        'Время конца мероприятия'
    )
    location = models.CharField(
        'Локация мероприятия',
        max_length=150
    )

    class Meta:
        verbose_name = 'Митап'
        verbose_name_plural = 'Митапы'

    def __str__(self):
        return f'Мероприятие {self.title}'


class Event(models.Model):

    title = models.CharField(
        max_length=100,
        verbose_name="Название",
    )

    speaker = models.ForeignKey(
        Speaker,
        verbose_name='Спикеры',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    time_start = models.TimeField(
        verbose_name='Время начала'
    )

    time_end = models.TimeField(
        verbose_name='Время окончания'
    )
    meetup = models.ForeignKey(
        Meetup,
        on_delete=models.CASCADE,
        verbose_name="Событие",
        related_name='events'
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.title


class Question(models.Model):
    text = models.TextField(
        max_length=200,
        verbose_name='Текст вопроса',
        blank=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Событие",
        related_name="questions"
    )
    asker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Спрашивающий'
    )
    time = models.DateTimeField(
        'Время появления вопроса',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'Вопрос от {self.asker}, на событие {self.event}'
