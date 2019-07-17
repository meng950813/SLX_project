from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from web.extensions import mail


def _send_async_mail(app, message):
    """另一个线程发送邮件"""
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, template, **kwargs):
    """
    发送邮件
    :param subject: 邮件主题
    :param to: 发送给谁/接收者
    :param template: 模板
    :param kwargs: 发送给模板的键值对
    :return:
    """
    message = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)

    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_reset_password_email(token, to):
    """
    发送重置密码的邮件
    :param token: 验证令牌
    :param to: 接收者
    :return:
    """
    send_mail(subject='重置密码', to=to, template='emails/reset_password', token=token)


def send_change_email_email(token, to):
    """
    发送重置邮箱的邮件
    :param token: 验证令牌
    :param to: 接收者
    :return:
    """
    send_mail(subject='改变邮箱', to=to, template='emails/change_email', token=token)

