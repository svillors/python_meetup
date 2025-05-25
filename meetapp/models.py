from django.db import models


class Speaker(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name="ФИО",
    )

    description = models.TextField(
        max_length = 100,
        verbose_name='Описание',
        blank=True
    )

    class Meta:
        verbose_name = 'Спикер'
        verbose_name_plural = 'Спикеры'

    

class Meetup(models.Model):
    
    title = models.CharField(
        max_length=100,
        verbose_name="Название",
    )

    date = models.DateField(verbose_name='Дата митапа')

    class Meta:
        verbose_name = 'Митап'
        verbose_name_plural = 'Митапы'


class Event(models.Model):

    title = models.CharField(
        max_length=100,
        verbose_name="Название",
    )

    speakers = models.ManyToManyField(
        Speaker, 
        through='EventSpeaker',
        verbose_name='Спикеры',
        blank=True
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


class Question(models.Model):
    
    text = models.TextField(
        max_length = 200,
        verbose_name='Текст вопроса',
        blank=True
    )

    event_name = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Событие", related_name="questions"
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

<<<<<<< Updated upstream
=======
    def __str__(self):
        return f'Вопрос от {self.asker}, на событие {self.event}'


class Application(models.Model):

    text = models.TextField(
        max_length=200,
        verbose_name='Текст заявки'
    )

    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подающий'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'Заявка от {self.applicant}, на роль спикера'
>>>>>>> Stashed changes
