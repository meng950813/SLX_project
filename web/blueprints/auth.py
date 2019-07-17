from flask import Blueprint, session, redirect, url_for, render_template, flash
from web.forms import LoginForm
import functools
from web.service import user_service
from web.config import AGNET_TYPE


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
            return redirect(url_for('auth.login'))
        return func(*args, **kw)
    return wrapper


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('school_agent.index'))

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
                return redirect(url_for('school_agent.index'))
            else:
                # TODO 企业商务主页
                flash('暂不支持企业商务登陆', 'danger')
                return render_template('login.html', form=form)
        flash('登录失败，请检测账号或者密码后重新输入', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
