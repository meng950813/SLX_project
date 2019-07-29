"""
author: xiaoniu
date: 2019-07-29
desc: 用作flask-wtf的表单类型 从原先的forms.py拆分得到
"""
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    """
    活动表单
    """
    title = StringField('活动名：', validators=[DataRequired()])
    location = StringField('活动地点：', validators=[DataRequired()])
    date = DateField('日期：')
    content = CKEditorField('内容：')
    submit = SubmitField('提交')

    def get_data(self):
        """从form表单中提取数据"""
        datum = {
            'title': self.title.data,
            'location': self.location.data,
            'date': self.date.data.strftime('%Y-%m-%d'),
            'content': self.content.data,
        }
        return datum

