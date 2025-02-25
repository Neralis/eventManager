from django.core.mail import send_mail

def send():
    send_mail(
        f'Вы зарегестрировались на мероприятие',
        'Спасибо за вашу активность!',
        'example@gmail.com',
        ['ner4corp@gmail.com'],
        fail_silently=False,
    )