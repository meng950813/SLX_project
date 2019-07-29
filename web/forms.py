"""
author: xiaoniu
date: 2019-07-22
desc: 用作flask-wtf的表单类型
"""
import json
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, \
    SelectField, SelectMultipleField, DateTimeField, HiddenField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo

from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG


class LoginForm(FlaskForm):
    """
    登录表单
    """
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128, message='密码最少为8位')])
    remember = BooleanField('七天免登陆')
    submit = SubmitField('登录')


class ScholarForm(FlaskForm):
    """
    老师个人信息表单
    """
    name = StringField('姓名：', validators=[DataRequired()])
    gender = SelectField('性别：', choices=[('', '未知'), ('男', '男'), ('女', '女')], coerce=str)
    birth_year = StringField('出生年份', validators=[Optional()])
    domain = HiddenField()

    school = SelectField('学校：', validators=[DataRequired()], coerce=str)
    institution = SelectField('学院：', validators=[DataRequired()], coerce=str)
    department = StringField('系：', validators=[Optional()])

    title = SelectField('职称：', choices=[('', '未知'), ('教授', '教授'), ('副教授', '副教授'),
                                        ('讲师', '讲师'), ('助教', '助教')], default='', coerce=str)
    honor = SelectMultipleField('荣誉头衔：', choices=[
        ('中国科学院院士', '中国科学院院士院士'), ('中国工程院院士', '中国工程院院士院士'), ('长江学者', '长江学者'),
        ('杰出青年', '杰出青年'), ('优秀青年', '优秀青年')], default='', coerce=str)
    phone_number = StringField('手机号：')
    office_number = StringField('办公电话：')
    email = StringField('邮箱：', validators=[Email(), Optional()])
    edu_exp = TextAreaField('教育经历：')
    work_exp = TextAreaField('工作经历：')
    submit = SubmitField('提交')

    def __init__(self, teacher_id, type_get, *args, **kwargs):
        """

        :param teacher_id:
        :param type_get:
        :param args:
        :param kwargs:
        """
        super(ScholarForm, self).__init__(*args, **kwargs)
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        cur_school = None
        cur_institution = None
        # 设置数据
        if teacher_id:
            if type_get:
                result = mongo_operator.get_collection('basic_info').find_one({'id': teacher_id}, {'_id': 0})
                self.set_data(result)
            else:
                result = mongo_operator.get_collection('basic_info').find_one({'id': teacher_id},
                                                                              {'school': 1, 'institution': 1})
            cur_school, cur_institution = result['school'], result['institution']
        # 获取所有的学校
        generator = mongo_operator.get_collection('school').find({}, {'_id': 0, 'name': 1})
        cur_school = self.set_schools(generator, cur_school)
        # 获取当前学校的所有院系
        school = mongo_operator.get_collection('school'). \
            find_one({'name': cur_school}, {'_id': 0, 'institutions': 1})
        self.set_institutions(school['institutions'], cur_institution)

    def set_data(self, datum):
        """
        将从数据库中获取的数据渲染到前端页面
        :param datum: dict
        :return:
        """
        self.name.data = datum['name']
        if 'gender' in datum:
            self.gender.data = datum['gender']
        if 'birth_year' in datum and datum['birth_year']:
            self.birth_year.data = datum['birth_year'].strip()

        if 'department' in datum:
            self.department.data = datum['department']

        self.title.data = datum['title'].strip()
        if 'honor' in datum:
            self.honor.data = datum['honor']
        if 'domain' in datum:
            self.domain.data = ';'.join(datum['domain'])

        self.email.data = datum['email'].strip()
        self.phone_number.data = datum['phone_number'].strip()
        self.office_number.data = datum['office_number'].strip()
        self.edu_exp.data = datum['edu_exp'].strip().replace("<br>", "\n")
        if "work_exp" in datum:
            self.work_exp.data = datum['work_exp'].strip().replace("<br>", "\n")

    def get_data(self):
        datum = {
            'name': self.name.data,
            'gender': self.gender.data,
            'birth_year': self.birth_year.data,
            'school': self.school.data,
            'institution': self.institution.data,
            'department': self.department.data,
            'title': self.title.data,
            'honor': self.honor.data,
            'email': self.email.data,
            'phone_number': self.phone_number.data,
            'office_number': self.office_number.data,
            'edu_exp': self.edu_exp.data,
            'work_exp': self.work_exp.data
        }
        if len(self.domain.data.strip()) == 0:
            datum['domain'] = []
        else:
            datum['domain'] = self.domain.data.split(';')

        return datum

    def set_schools(self, schools, cur_school):
        self.school.choices = [(school['name'], school['name']) for school in schools]
        if cur_school:
            self.school.data = cur_school
        elif self.school.data != 'None':
            cur_school = self.school.data
        else:
            cur_school = self.school.choices[0][0]
        return cur_school

    def set_institutions(self, institutions, cur_institution):
        self.institution.choices = [(institution['name'], institution['name']) for institution in institutions]
        if cur_institution:
            self.institution.data = cur_institution


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


class ActivityForm(FlaskForm):
    """
    活动表单
    """
    title = StringField('活动名：', validators=[DataRequired()])
    location = StringField('活动地点：', validators=[DataRequired()])
    date = DateTimeField('日期：')
    content = TextAreaField('内容：')


class ProjectForm(FlaskForm):
    """
    项目表单
    """
    name = StringField('项目名称', validators=[DataRequired()])
    project_type = SelectField('项目类型',
                               choices=[('省（部）级鉴定', '省（部）级鉴定'),
                                        ('授权发明专利', '授权发明专利'), ('国外技术', '国外技术'),
                                        ('其他', '其他')], default='省（部）级鉴定', coerce=str)
    fund = FloatField('项目资金', validators=[DataRequired()])
    start_time = DateField('起止时间', validators=[DataRequired()])
    end_time = DateField('截至时间', validators=[DataRequired()])
    members = HiddenField()

    company = StringField('支撑单位', validators=[DataRequired()])
    content = TextAreaField('项目简介', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

    def get_data(self):
        datum = {
            'name': self.name.data,
            'project_type': self.project_type.data,
            'fund': self.fund.data,
            'start_time': ProjectForm.date2datetime(self.start_time.data),
            'end_time': ProjectForm.date2datetime(self.end_time.data),
            'members': json.loads(self.members.data),
            'company': self.company.data,
            'content': self.content.data,
        }
        return datum

    @staticmethod
    def date2datetime(date):
        return datetime.datetime(date.year, date.month, date.day)
