from itsdangerous import URLSafeTimedSerializer

from saby_combat import app


def generate_verification_token(email_adress) -> str:
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email_adress, salt=app.config["SECURITY_PASSWORD_SALT"])


# Возвращает str: email, если подтверждение прошло успешно,
# иначе - False
def confirm_verification_token(verification_token, expiration=6000) -> str:
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email_adress = serializer.loads(verification_token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration)
        return email_adress
    except Exception as ex:
        raise ex