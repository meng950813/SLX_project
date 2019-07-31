"""
author: xiaoniu
date: 2019-07-29
desc: 用作flask-wtf的表单类型 从原先的forms.py拆分得到
"""
import json
import datetime
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, DateField, HiddenField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    """
    活动表单
    """
    title = StringField('活动名：', validators=[DataRequired()])
    location = StringField('活动地点：', validators=[DataRequired()])
    date = DateField('日期：', validators=[DataRequired()])
    content = CKEditorField('内容：', validators=[DataRequired()])
    # 负责接收关系
    relationship = HiddenField()

    def get_data(self):
        """从form表单中提取数据"""
        datum = {'title': self.title.data, 'location': self.location.data, 'date': self.date.data.strftime('%Y-%m-%d'),
                 'content': self.content.data, 'relationship': json.loads(self.relationship.data)}
        # 获取关系
        return datum

    def set_data(self, datum):
        self.title.data = datum['title']
        self.location.data = datum['location']
        self.date.data = datetime.datetime.strptime(datum['date'], '%Y-%m-%d')
        self.content.data = datum['content']
        self.relationship.data = json.dumps(datum['relationship'], ensure_ascii=False)
