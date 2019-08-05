import os
from flask import Flask, render_template
from flask_login import current_user

from web.settings import configuration
from web.blueprints.school_agent import school_agent_bp
from web.blueprints.scholar import scholar_bp
from web.blueprints.visit_record import visit_record_bp
from web.blueprints.schedule import schedule_bp
from web.blueprints.auth import auth_bp
from web.blueprints.reminder import reminder_bp
from web.blueprints.activity import activity_bp
from web.blueprints.school import school_bp
from web.extensions import bootstrap, csrf, moment, mail, login_manager, ckeditor
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
from web.settings import Message


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', "development")

    app = Flask('web')
    app.config.from_object(configuration[config_name])

    # 注册日志处理器
    register_logger(app)
    # 初始化扩展
    register_extensions(app)
    # 注册蓝图
    register_blueprints(app)
    # 注册错误处理函数
    register_errors(app)
    # 注册模板上下文处理函数
    register_template_context(app)

    return app


def register_logger(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app=app)


def register_blueprints(app):
    app.register_blueprint(school_agent_bp)
    app.register_blueprint(scholar_bp, url_prefix='/scholar')
    app.register_blueprint(auth_bp)
    app.register_blueprint(visit_record_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(activity_bp, url_prefix='/activity')
    app.register_blueprint(school_bp, url_prefix='/school')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html', description="会话过期或失效，请返回上一页重试"), 400

    @app.errorhandler(404)
    def bad_request(e):
        return render_template('errors/404.html'), 404


def register_template_context(app):
    """注册模板上下文，使得变量可以在模板中使用"""
    @app.context_processor
    def make_template_context():
        # 如果登录，则尝试拉取未读信息
        unread_msg = 0

        if current_user.is_authenticated:
            uid = current_user.id
            mongo_operator = MongoOperator(**MongoDB_CONFIG)
            unread_msg = mongo_operator.find({"to_id": uid, "state": Message.UNCHECKED}, "message").count()

        return dict(unread_msg=unread_msg)


