from flask import Blueprint, render_template, request, flash, abort
from flask_login import current_user
import web.service.basic_info_service as basic_info_service
import datetime
import json

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
from web.forms.scholar import ScholarForm, ProjectForm
from web.utils import redirect_back

scholar_bp = Blueprint('scholar', __name__)


@scholar_bp.route('/detail/<int:teacher_id>')
@login_required
def scholar_info(teacher_id):
    """
    获取专家个人信息
    :param teacher_id:
    :return:
    """
    # 返回json 序列化后的数据
    teacher = basic_info_service.get_info(teacher_id)
    # 当老师id不存在时，直接报404
    if teacher is None:
        return abort(404)

    # 获取拜访记录
    visit_list = None
    try:
        mongo = MongoOperator(**MongoDB_CONFIG)
        collection = mongo.get_collection("visit_record")
        user_id = current_user.id
        # 找到对应的拜访记录信息, 按时间排序, 最多5个
        visit_info = collection.find({"user_id": user_id, "status": 1, "teacher_id": teacher_id},
                            {"_id": 0, "date": 1, "title": 1, "content": 1, "user_name": 1}).sort("date", -1).limit(5)
        # 转成列表 
        visit_list = list(visit_info)
    except Exception as e:
        print('get_visit_info error:%s' % e)

    return render_template('scholar/detail.html', teacher=teacher, visit_list=visit_list)


@scholar_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    """
    老师信息反馈页面
    GET 返回当前页面
    POST 进行数据库操作
    :return:
    """
    teacher_id = request.args.get('tid', type=int, default=None)
    # 当前类型 添加or修改 add modify
    cur_type = 'modify' if teacher_id else 'add'
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    form = ScholarForm(teacher_id, type_get=request.method == 'GET')

    if request.method == 'POST':
        # 出现错误，则交给flash
        if not form.validate():
            warning = []
            for _, errors in form.errors.items():
                warning.extend(errors)
            flash(','.join(warning), 'warning')
        else:
            datum = form.get_data()
            datum.update({
                'type': cur_type, 'status': 1, 'username': current_user.name,
                'timestamp': datetime.datetime.utcnow(), 'teacher_id': teacher_id
            })
            # 写入数据库
            result = mongo_operator.db['agent_feedback'].insert_one(datum)
            flash('操作成功，感谢您的反馈', 'success')

            return redirect_back()

    return render_template('scholar/teacher_feedback.html', form=form, cur_type=cur_type)


@scholar_bp.route('/search', methods=['GET'])
@login_required
def search():
    """
    老师检索
    :return:
    """
    teachers = []
    teacher_name = ""

    if 'teacher-name' in request.args:
        teacher_name = request.args.get('teacher-name')
        # 获取老师列表
        teachers = get_teachers(teacher_name)

    return render_template('scholar/search.html', teachers=teachers, teacher_name=teacher_name)


@scholar_bp.route('/get_teachers/<teacher_name>')
@login_required
def get_teachers(teacher_name):
    """
    根据老师的名字进行数据库的搜索
    :param teacher_name: 老师名字
    :return: 如果request.args存在is_json且为True,则返回json格式的字符串，否则直接返回python数组
    """
    # 是否把结果转换成json格式的字符串,默认为False
    result = None
    is_json = request.args.get('is_json', type=bool, default=False)
    # 是否进行模糊查询
    is_like = request.args.get('is_like', type=bool, default=False)

    try:
        # 查询数据库
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        # 模糊查询
        if is_like:
            condition = {'name': {'$regex': teacher_name + '.*?'}}
        else:
            condition = {'name': teacher_name}
        scope = {'title': 1, 'school': 1, 'institution': 1, 'name': 1, '_id': 0, 'id': 1}
        generator = mongo_operator.get_collection('basic_info').find(condition, scope)
        teachers = list(generator)
        result = json.dumps(teachers) if is_json else teachers
    except Exception as e:
        print('error raised when get teacher: %s' % e)

    return result


@scholar_bp.route('/get_institutions/<school>', methods=['GET'])
@login_required
def get_institutions(school):
    """
    根据学校的名称获取学院列表
    :param school:
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取当前学校的所有院系
    condition = {'name': school}
    school = mongo_operator.get_collection('school').find_one(condition, {'_id': 0, 'institutions': 1})

    return json.dumps(school['institutions'])


@scholar_bp.route('/project', methods=['GET', 'POST'])
@login_required
def project_feedback():
    """
    项目反馈
    :return:
    """
    form = ProjectForm()
    mongo = MongoOperator(**MongoDB_CONFIG)
    # 获取所有的学校
    generator = mongo.get_collection('school').find({}, {'_id': 0, 'name': 1})
    schools = [school['name'] for school in generator]
    cur_school = schools[0]
    # 获取当前学校的所有院系
    school = mongo.get_collection('school').find_one({'name': cur_school}, {'_id': 0, 'institutions': 1})
    institutions = [result['name'] for result in school['institutions']]

    if request.method == 'POST':
        # 出现错误，则交给flash
        if not form.validate():
            flash('数据输入有误，请确认后输入', 'warning')
        else:
            datum = form.get_data()
            datum.update({'timestamp': datetime.datetime.utcnow(), 'username': current_user.name, 'status': 1})
            # 写入数据库
            result = mongo.db['project_feedback'].insert_one(datum)
            flash('操作成功，感谢您的反馈', 'success')

            return redirect_back()

    return render_template('scholar/project_feedback.html', form=form, schools=schools, institutions=institutions)
