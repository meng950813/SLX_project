"""
author: xiaoniu
date: 2019-07-29
desc: 用作flask-wtf的表单类型 从原先的forms.py拆分得到
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    """
    活动表单
    """
    title = StringField('活动名：', validators=[DataRequired()])
    location = StringField('活动地点：', validators=[DataRequired()])
    date = DateTimeField('日期：')
    content = TextAreaField('内容：')


