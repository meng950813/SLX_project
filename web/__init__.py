import os
from flask import Flask, render_template
from web.settings import configuration
from web.blueprints.school_agent import school_agent_bp
# from web.extensions import db, mail, bootstrap, moment, ckeditor, migrate


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', "development")

    app = Flask('web')
    app.config.from_object(configuration[config_name])

    # 注册日志处理器
    register_logging(app)
    # 初始化扩展
    register_extensions(app)
    # 注册蓝图
    register_blueprints(app)
    # 注册错误处理函数
    register_errors(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    app.register_blueprint(school_agent_bp)


def register_blueprints(app):
    pass


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400


