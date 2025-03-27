# -*- coding: utf-8 -*-
import sys
import traceback
import random
import string
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from participantApp.models import Participants
from eventApp.models import Event
from reviewApp.models import Review  # Добавлен импорт модели отзывов

# Получаем модель CustomUser
CustomUser = get_user_model()

# Функция для генерации случайной строки
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Функция для генерации случайной даты рождения
def random_birthday():
    start_date = datetime(1970, 1, 1)
    end_date = datetime(2005, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Функция для создания пользователей по умолчанию
def create_default_users():
    print("Проверка и создание пользователей по умолчанию...")
    try:
        remove_user, created = CustomUser.objects.get_or_create(
            username='default_remove_user',
            defaults={
                'email': 'remove_user@gmail.com',
                'date_birthday': '2025-03-27',
                'phone': '+12345678911'
            }
        )
        if created:
            print("Создан пользователь default_remove_user")

        if not CustomUser.objects.filter(username='root').exists():
            root_user = CustomUser.objects.create_superuser(
                username='root',
                email='root@example.com',
                password='root'
            )
            print("Создан суперпользователь root")
        else:
            print("Суперпользователь root уже существует")

    except Exception as e:
        print(f"Ошибка при создании пользователей: {e}")
        traceback.print_exc()

# Функция для создания 100 случайных пользователей
def create_random_users():
    existing_users = CustomUser.objects.count()
    if existing_users >= 100:
        print(f"Уже есть {existing_users} пользователей. Новые не создаем.")
        return

    users_to_create = []
    for i in range(1, 101):
        users_to_create.append(CustomUser(
            username=f'user_{random_string(6)}_{i}',
            email=f'user_{random_string(4)}_{i}@gmail.com',
            date_birthday=random_birthday(),
            phone=f'+12345678{i:03d}'
        ))

    CustomUser.objects.bulk_create(users_to_create, ignore_conflicts=True)
    print(f"{len(users_to_create)} уникальных пользователей успешно созданы!")

# Функция для получения или создания события "test"
def get_or_create_test_event():
    print("Запуск get_or_create_test_event")
    start_date = timezone.now() + timezone.timedelta(days=1)
    end_date = timezone.now() + timezone.timedelta(days=2)

    try:
        event, created = Event.objects.get_or_create(
            title='test',
            defaults={
                'description': 'Тестовое мероприятие',
                'date_start': start_date,
                'date_end': end_date,
                'age_limit': 0,
                'organizer': CustomUser.objects.first(),
                'event_format': 'Online',
                'registration_status': True,
                'participants_limit': 100,
                'available_places': 100,
                'location_online': 'https://example.com/test-event',
                'is_active': True,
            }
        )
        if not created and event.available_places == 0:
            print("Событие уже существует, но доступных мест нет. Сбрасываем до 100.")
            event.available_places = 100
            event.save()
        print(f"Событие 'test' {'создано' if created else 'уже существовало'} с ID: {event.id}")
        print(f"Доступных мест изначально: {event.available_places}")
        return event
    except Exception as e:
        print(f"Ошибка в get_or_create_test_event: {e}")
        traceback.print_exc()
        raise

# Функция для добавления пользователей в событие
def add_users_to_event():
    print("Запуск add_users_to_event")
    try:
        with transaction.atomic():
            all_users = list(CustomUser.objects.exclude(date_birthday__isnull=True))
            print(f"Найдено пользователей с датой рождения: {len(all_users)}")
            if not all_users:
                print("Ошибка: в базе нет пользователей с датой рождения.")
                return

            test_event = get_or_create_test_event()
            existing_participants = set(Participants.objects.filter(event=test_event).values_list('user_id', flat=True))
            print(f"Участников до запуска: {len(existing_participants)}")

            organizer = test_event.organizer
            participants_to_add = []
            available_places = test_event.available_places

            for user in all_users:
                if user == organizer:
                    print(f"Пропускаем пользователя {user.username}, так как он организатор.")
                    continue
                if user.id in existing_participants:
                    print(f"Пользователь {user.username} уже является участником.")
                    continue
                if available_places > 0:
                    participants_to_add.append(Participants(
                        event=test_event,
                        user=user,
                        created=timezone.now()
                    ))
                    available_places -= 1
                else:
                    print("Лимит участников исчерпан")
                    break

            if participants_to_add:
                Participants.objects.bulk_create(participants_to_add)
                test_event.available_places = available_places
                test_event.save()
                print(f"Добавлено {len(participants_to_add)} новых участников.")

            final_participants = Participants.objects.filter(event=test_event).count()
            print(f"Итог: добавлено {len(participants_to_add)} новых участников к событию 'test'.")
            print(f"Всего участников после выполнения: {final_participants}")
            print(f"Осталось доступных мест: {test_event.available_places}")

    except Exception as e:
        print(f"Ошибка в add_users_to_event: {e}")
        traceback.print_exc()

# Функция для добавления отзывов от участников тестового мероприятия
def add_reviews():
    """Добавляет отзывы от всех участников тестового мероприятия."""
    print("Запуск add_reviews")
    try:
        event = Event.objects.filter(title="test").first()
        if not event:
            print("Тестовое мероприятие не найдено!")
            return

        participants = Participants.objects.filter(event=event)
        for participant in participants:
            if Review.objects.filter(event=event, participant=participant).exists():
                print(f"Отзыв от {participant} уже существует.")
                continue

            review = Review.create_review(
                event=event,
                participant=participant,
                text=f"Отзыв от {participant}",
                rating=random.randint(1, 5)
            )
            print(f"Добавлен отзыв: {review}")

    except Exception as e:
        print(f"Ошибка при добавлении отзывов: {e}")
        traceback.print_exc()

# Выполняем скрипт
if __name__ == "__main__":
    print("Скрипт запущен")
    create_default_users()
    create_random_users()
    add_users_to_event()
    add_reviews()  # Добавлена функция добавления отзывов
    print("Скрипт завершен")
