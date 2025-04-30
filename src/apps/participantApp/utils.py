from src.utils.constants.email_constants import SEND_MAIL_REGISTER_ON_EVENT_TITLE, SEND_MAIL_REGISTER_ON_EVENT_TEXT
from src.utils.utils import send_mail_users


def send_mail_after_registration_on_event(email: str, event_title: str) -> None:
    """
    Функция для отправки сообщений пользователям после регистрации на мероприятие.
    Args:
        email: email участника
        event_title: название мероприятия
    """

    subject = f'{SEND_MAIL_REGISTER_ON_EVENT_TITLE}{event_title}'
    message = SEND_MAIL_REGISTER_ON_EVENT_TEXT
    send_mail_users(subject, message, [email])