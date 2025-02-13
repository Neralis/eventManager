import string
from random import choice


def get_random_string():
    return ''.join(choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))