import string
from random import choices


def get_random_string():
    """Функция для генерации рандомной строки. Используется для создания уникальных слагов."""
    return ''.join(choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=6))