# Generated by Django 4.2 on 2025-05-25 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetapp', '0005_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, max_length=200, verbose_name='Текст вопроса')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetapp.user', verbose_name='Подающий')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
    ]
