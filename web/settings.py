import os
import uuid
import datetime
from web.config import MAIL_CONFIG


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


AGNET_TYPE = {
    "SCHOOL_AGENT": "0",
    "BUSINESS_AGENT": "1"
}


class BaseConfig(object):
    # wtform库用于CSRF
    SECRET_KEY = os.getenv('SECRET_KEY', uuid.uuid4().hex)
    # 邮件相关
    MAIL_SERVER = MAIL_CONFIG['server']
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = MAIL_CONFIG['username']
    MAIL_PASSWORD = MAIL_CONFIG['password']
    MAIL_DEFAULT_SENDER = MAIL_CONFIG['username']
    MAIL_SUBJECT_PREFIX = '三螺旋 '

    # flask-login 会话过期时长
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=7)


class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


configuration = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
