from flask import Blueprint, session, redirect, url_for, render_template, flash, request
import functools

from web.utils import redirect_back, generate_token, validate_token
from web.forms import LoginForm, ForgetPasswordForm, ResetPasswordForm
from web.settings import Operations, AGNET_TYPE
from web.emails import send_reset_password_email
import web.service.user_service as user_service


auth_bp = Blueprint('auth', __name__)


def login_required(func):
    """
    装饰函数，如果需要某函数需要登陆后操作，则可以装饰上此函数
    如@login_required
    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        # 当前未登陆
        user = session.get('username')

        if user is None:
            return redirect(url_for('auth.login', next=request.full_path))
        return func(*args, **kw)
    return wrapper


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect_back('school_agent.index')

    form = LoginForm()
    # 提交表单
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        user = user_service.check_user(username, password)
        # 检验账号密码
        if user:
            session['username'] = user["name"]
            session['uid'] = user["id"]
            session["type"] = user["type"]
            # flash('登录成功，欢迎回来', 'success')
            if user["type"] == AGNET_TYPE["SCHOOL_AGENT"]:
                return redirect_back('school_agent.index')
            else:
                # TODO 企业商务主页
                flash('暂不支持企业商务登陆', 'danger')
                return render_template('auth/login.html', form=form)
        flash('登录失败，请检测账号或者密码后重新输入', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    """
    忘记密码
    :return:
    """
    form = ForgetPasswordForm()

    if form.validate_on_submit():
        # 获取邮箱 并查询数据库
        email = form.email.data.lower()
        user = user_service.get_user_by_email(email)

        # 发送到邮箱
        if user:
            token = generate_token(user, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(token=token, to=email, user=user)
            flash('重置密码邮件已发送到您的邮箱，请注意查收.', 'info')
            return redirect(url_for('.login'))

        flash('邮箱输入有误，请重新输入.', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/forget_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        # 数据库查询
        user = user_service.get_user_by_email(email)

        if user is None:
            return redirect(url_for('school_agent.index'))
        # 传入新密码
        if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD, new_password=form.password.data):
            flash('Password updated.', 'success')
            return redirect(url_for('.login'))
        else:
            flash('Invalid or expired token.', 'danger')
            return redirect(url_for('.forget_password'))

    return render_template('auth/reset_password.html', form=form)
