from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, \
    SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo

from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128, message='密码最少为8位')])
    remember = BooleanField('七天免登陆')
    submit = SubmitField('登录')


class ScholarForm(FlaskForm):
    name = StringField('姓名：', validators=[DataRequired()])
    gender = SelectField('性别：', choices=[('男', '男'), ('女', '女')], coerce=str)
    birth_year = StringField('出生年份', validators=[Optional()])

    school = SelectField('学校：', validators=[DataRequired()], coerce=str)
    institution = SelectField('学院：', validators=[DataRequired()], coerce=str)
    department = StringField('系：', validators=[Optional()])

    title = SelectField('头衔：', choices=[('', '未知'), ('教授', '教授'), ('副教授', '副教授'), ('讲师', '讲师'), ('助教', '助教')], default='', coerce=str)
    honor = SelectMultipleField('荣誉头衔：', choices=[('院士', '院士'), ('长江学者', '长江学者'), ('杰出青年', '杰出青年')], default='', coerce=str)
    phone_number = StringField('手机号：')
    office_number = StringField('办公电话：')
    email = StringField('邮箱：', validators=[Email(), Optional()])
    edu_exp = TextAreaField('教育经历：')
    submit = SubmitField('提交')

    def __init__(self, teacher_id, *args, **kwargs):
        super(ScholarForm, self).__init__(*args, **kwargs)
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        cur_school = None
        cur_institution = None
        # 设置数据
        if teacher_id:
            result = mongo_operator.get_collection('basic_info').find_one({'id': teacher_id}, {'_id': 0})
            self.set_data(result)
            cur_school, cur_institution = result['school'], result['institution']
        # 获取所有的学校
        generator = mongo_operator.get_collection('school').find({}, {'_id': 0, 'name': 1})
        cur_school = self.set_schools(generator, cur_school)
        # 获取当前学校的所有院系
        school = mongo_operator.get_collection('school'). \
            find_one({'name': cur_school}, {'_id': 0, 'institutions': 1})
        self.set_institutions(school['institutions'], cur_institution)

    def set_data(self, datum):
        self.name.data = datum['name']
        if 'gender' in datum:
            self.gender.data = datum['gender']
        if 'birth_year' in datum and datum['birth_year']:
            self.birth_year.data = datum['birth_year'].strip()

        if 'department' in datum:
            self.department.data = datum['department']

        self.title.data = datum['title']
        if 'honor' in datum:
            self.honor.data = datum['honor']

        self.email.data = datum['email'].strip()
        self.phone_number.data = datum['phone_number'].strip()
        self.office_number.data = datum['office_number'].strip()
        self.edu_exp.data = datum['edu_exp']

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
        }
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
    email = StringField('', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField('下一步')


class ResetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class ActivityForm(FlaskForm):
    title = StringField('活动名：', validators=[DataRequired()])
    location = StringField('活动地点：', validators=[DataRequired()])
    date = DateTimeField('日期：')
    content = TextAreaField('内容：')
