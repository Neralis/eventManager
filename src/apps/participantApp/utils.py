from src.utils.constants.email_constants import SEND_MAIL_REGISTER_ON_EVENT_TITLE, SEND_MAIL_REGISTER_ON_EVENT_TEXT, \
    SEND_MAIL_PARTICIPANT_AFTER_DEL_TITLE, SEND_MAIL_PARTICIPANT_AFTER_DEL_TEXT, SEND_MAIL_PARTICIPANT_AFTER_DEL_REASON, \
    SEND_MAIL_PARTICIPANT_AFTER_DEL_RELATION
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


def send_email_users_after_delete(email_participant: str, email_organizer: str, event_title: str, reason: str = None):
    """
    Функция для отправки сообщений пользователям,
    после того, как организатор удалит их как участников мероприятия.
    Args:
        email_participant: email участника мероприятия
        email_organizer: email организатора мероприятия
        reason: причина удаления
        event_title: название мероприятия
    """

    subject = f'{SEND_MAIL_PARTICIPANT_AFTER_DEL_TITLE}{event_title}'
    message = f'{SEND_MAIL_PARTICIPANT_AFTER_DEL_TEXT}\n'
    if reason:
        message += f'{SEND_MAIL_PARTICIPANT_AFTER_DEL_REASON}{reason}.'
    message += f'{SEND_MAIL_PARTICIPANT_AFTER_DEL_RELATION}{email_organizer}'
    send_mail_users(subject, message, [email_participant])