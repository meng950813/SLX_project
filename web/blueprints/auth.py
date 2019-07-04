from flask import Blueprint, session, redirect, url_for, render_template
from web.forms import LoginForm


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('school_agent.homepage'))

    form = LoginForm()
    # 提交表单
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        # 检验账号密码
    return render_template('login.html', form=form)
