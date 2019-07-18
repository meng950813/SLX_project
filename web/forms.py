from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, \
    SelectField, SelectMultipleField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128, message='密码最少为8位')])
    remember = BooleanField('七天免登陆')
    submit = SubmitField('登录')


class ScholarForm(FlaskForm):
    school = StringField('学校：', validators=[DataRequired()])
    institution = StringField('学院：', validators=[DataRequired()])
    name = StringField('姓名：', validators=[DataRequired()])
    birth_year = IntegerField('出生年份', validators=[Optional()])
    title = SelectField('头衔：', choices=[('', '未知'), ('教授', '教授'), ('副教授', '副教授'), ('讲师', '讲师'), ('助教', '助教')], default='', coerce=str)
    honor = SelectMultipleField('荣誉头衔：', choices=[('院士', '院士'), ('长江学者', '长江学者'), ('杰出青年', '杰出青年')], default='', coerce=str)
    phone_number = StringField('手机号：')
    office_number = StringField('办公电话：')
    email = StringField('邮箱：', validators=[Email(), Optional()])
    edu_exp = TextAreaField('教育经历：')
    submit = SubmitField('提交')

    def set_data(self, datum):
        self.name.data = datum['name']
        self.school.data = datum['school']
        self.institution.data = datum['institution']
        self.birth_year.data = datum['birth_year'].strip()
        self.title.data = datum['title']
        if 'honors' in datum:
            self.honor.data = datum['honors']

        self.email.data = datum['email'].strip()
        self.phone_number.data = datum['phone_number'].strip()
        self.office_number.data = datum['office_number'].strip()
        self.edu_exp.data = datum['edu_exp']

    def get_data(self):
        datum = {
            'name': self.name.data,
            'school': self.school.data,
            'institution': self.institution.data,
            'birth_year': self.birth_year.data,
            'title': self.title.data,
            'honors': self.honor.data,
            'email': self.email.data,
            'phone_number': self.phone_number.data,
            'office_number': self.office_number.data,
            'edu_exp': self.edu_exp.data,
        }
        return datum


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
