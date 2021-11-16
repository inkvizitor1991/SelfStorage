# Generated by Django 3.2.9 on 2021-11-16 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(unique=True, verbose_name='ID пользователя в сети')),
                ('name', models.CharField(max_length=10, verbose_name='Псевдоним')),
                ('first_name', models.CharField(blank=True, max_length=10, verbose_name='Имя пользователя')),
                ('last_name', models.CharField(blank=True, max_length=10, null=True, verbose_name='Фамилия пользователя')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон пользователя')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время получения')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='agent_bot.profile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Заказы',
                'verbose_name_plural': 'Заказы',
                'ordering': ['created_at'],
            },
        ),
    ]
