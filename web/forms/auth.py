"""
author: xiaoniu
date: 2019-07-29
desc: 用作flask-wtf的表单类型 从原先的forms.py拆分得到
主要包含登录表单、忘记密码表单和重置密码表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email,EqualTo


class LoginForm(FlaskForm):
    """
    登录表单
    """
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128, message='密码最少为8位')])
    remember = BooleanField('七天免登陆')
    submit = SubmitField('登录')


class ForgetPasswordForm(FlaskForm):
    """
    忘记密码表单
    """
    email = StringField('', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField('下一步')


class ResetPasswordForm(FlaskForm):
    """
    重置密码表单
    """
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认')
