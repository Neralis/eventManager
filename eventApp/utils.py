import string
from random import choices


def get_random_string():
    return ''.join(choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=6))