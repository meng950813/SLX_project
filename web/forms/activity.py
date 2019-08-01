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
from wtforms.validators import DataRequired, ValidationError

from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


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

    def __int__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        # 用于保存活动所产生的结果
        self.results = None

    def get_data(self):
        """从form表单中提取数据"""
        datum = {'title': self.title.data, 'location': self.location.data, 'date': self.date.data.strftime('%Y-%m-%d'),
                 'content': self.content.data, 'relationship': self.results}
        # 获取关系
        return datum

    def set_data(self, datum):
        """根据datum传递的值填充表单"""
        self.title.data = datum['title']
        self.location.data = datum['location']
        self.date.data = datetime.datetime.strptime(datum['date'], '%Y-%m-%d')
        self.content.data = datum['content']
        self.relationship.data = json.dumps(datum['relationship'], ensure_ascii=False)

    def validate_relationship(self, field):
        """
        自定义验证器，会验证relationship字段的值与数据库的值是否匹配
        :param field: relationship字段
        当id未找到或者名称等不匹配时都会验证失败
        当验证不通过会抛出ValidateError错误
        """
        self.results = json.loads(field.data)
        ids = [result['teacherID'] for result in self.results]
        mongo = MongoOperator(**MongoDB_CONFIG)
        collection = mongo.get_collection('basic_info')
        # 验证id是否和名字 学校 学院匹配
        teachers = collection.find({'id': {'$in': ids}}, {'_id': 0, 'id': 1, 'name': 1, 'school': 1, 'institution': 1})
        # 验证通过的个数
        nums = 0
        for teacher in teachers:
            for result in self.results:
                if teacher['id'] == result['teacherID']:
                    if teacher['school'] != result['school'] or teacher['name'] != result['name'] or\
                            teacher['institution'] != result['institution']:
                        raise ValidationError('合作关系验证失败，请确定老师后重试')
                    else:
                        nums += 1

        if nums != len(ids):
            raise ValidationError('合作关系验证失败，请确定老师后重试')
