import os

app_dir = os.path.abspath(os.path.dirname(__file__))

default_database_uri = 'postgresql://saby_combat_dev:123poi098@localhost:5432/saby_combat'
default_security_password_salt = 'nikto-nikogda-ne-uznaet'
default_mail_server = 'smtp.gmail.com'
default_mail_username = 'youremail@gmail.com'
default_mail_password = 'some-app-password'


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or default_security_password_salt
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or default_mail_server
    MAIL_PORT = os.environ.get('MAIL_PORT') or '465'
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_DEBUG = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or default_mail_username
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or default_mail_password
    MAIL_DEFAULT_SENDER = MAIL_USERNAME


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') or default_database_uri


class TestingConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI') or default_database_uri


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI') or default_database_uri
