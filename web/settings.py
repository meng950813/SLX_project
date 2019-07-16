import os
from web.config import MAIL_CONFIG


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    # wtform库用于CSRF
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')
    # 邮件相关
    MAIL_SERVER = MAIL_CONFIG['server']
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = MAIL_CONFIG['username']
    MAIL_PASSWORD = MAIL_CONFIG['password']
    MAIL_DEFAULT_SENDER = ('三螺旋', MAIL_CONFIG['sender'])


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
