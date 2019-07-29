from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager
from flask_ckeditor import CKEditor

from web.service import user_service

bootstrap = Bootstrap()
csrf = CSRFProtect()
moment = Moment()
mail = Mail()
login_manager = LoginManager()
ckeditor = CKEditor()

# 当访问到受login_required时默认跳转到下面的视图
login_manager.login_view = 'auth.login'
login_manager.login_message = u'请先登录'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """用于从存储在session中的用户ID重新加载用户对象"""
    return user_service.get_user_by_id(user_id)
