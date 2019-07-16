from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, \
    SelectField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Optional


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128, message='密码最少为8位')])
    remember = BooleanField('记住我')
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

