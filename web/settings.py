import os
import datetime
from web.config import MAIL_CONFIG


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class Message:
    """消息发送类型"""
    UNCHECKED = 1
    CHECKED = 0


AGNET_TYPE = {
    "SCHOOL_AGENT": "0",
    "BUSINESS_AGENT": "1"
}


class BaseConfig(object):
    # wtform库用于CSRF
    SECRET_KEY = os.getenv('SECRET_KEY', "secret key")
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
    # flask-ckeditor相关
    # CKEditor包类型 (basic standard full)
    CKEDITOR_PKG_TYPE = 'full'
    # 不使用本地资源
    CKEDITOR_SERVE_LOCAL = False
    # 使用简体中文
    CKEDITOR_LANGUAGE = 'zh-cn'
    # 对图片上传开启CSRF 保护
    CKEDITOR_ENABLE_CSRF = True
    # 处理文件上传的URL
    CKEDITOR_FILE_UPLOADER = '/activity/upload'
    # 额外的插件
    # CKEDITOR_EXTRA_PLUGINS = ['image2']
    # 图片文件上传保存路径
    IMAGE_SAVE_PATH = os.path.join(basedir, 'uploads')


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
