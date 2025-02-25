import jwt
import datetime
from django.conf import settings
from django.utils import timezone

def generate_token(email, event_id):
    payload = {
        'email': email,
        'event_id': event_id,
        'exp': timezone.now() + datetime.timedelta(days=7),  # 7 дней
        'iat': timezone.now()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def validate_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload['email'], payload['event_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None, None
