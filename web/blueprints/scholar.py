from flask import Blueprint, render_template, session, request, flash
from web.service.basic_info_service import search_teacher_basic_info
import datetime
import json

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
from web.forms import ScholarForm
from web.blueprints.school_agent import get_institutions_list
from web.utils import redirect_back

scholar_bp = Blueprint('scholar', __name__)


@scholar_bp.route('/scholar/<int:teacher_id>')
@login_required
def scholar_info(teacher_id):
    """
    专家个人信息
    :param teacher_id:
    :return:
    """
    # 返回json 序列化后的文件
    teacher_basic_info = search_teacher_basic_info(teacher_id)
    length = [0, 0]

    # 计算该教师所拥有的基金的数目，并将其加到列表中，用以传送给前端
    if "funds" in teacher_basic_info:
        length[0] = len(teacher_basic_info["funds"])

    # 计算该教师所拥有的专利
    if "patent" in teacher_basic_info:
        length[1] = len(teacher_basic_info["patent"])

    # 计算教师年龄
    birth_year = teacher_basic_info["birth_year"]
    if birth_year == " ":
        age = " "
    else:
        year = datetime.datetime.now().year
        age = year - int(birth_year)

    return render_template('scholar/detail.html', teacher_basic_info=teacher_basic_info, length=length, age=age)


@scholar_bp.route('/feedback', methods=['POST'])
@login_required
def agent_feedback():
    """
    保存商务反馈的信息
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)

    back = mongo_operator.db['agent_feedback'].insert_one(
        {
            "user_id": session['uid'],
            'title': request.form.get('title'),
            'type': request.form.get('type'),
            'target': request.form.get('target'),
            'content': request.form.get('content').replace("\n", "<br>"),
            "status": 0
        })

    print(back.inserted_id)
    if back.inserted_id:
        return json.dumps({'success': True})
    return json.dumps({"success": False})


@scholar_bp.route('/info_feedback', methods=['GET', 'POST'])
@login_required
def info_feedback():
    form = ScholarForm()

    teacher_id = request.args.get('tid', type=int, default=None)
    # 当前类型 add modify
    cur_type = 'modify' if teacher_id else 'add'

    # if form.validate_on_submit():
    if request.method == 'GET' and teacher_id:
        # 传入数据库
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        result = mongo_operator.db['basic_info'].find_one({'id': teacher_id}, {'_id': 0})
        # 设置数据
        form.set_data(result)

    elif request.method == 'POST':
        # 出现错误，则交给flash
        if not form.validate():
            warning = []
            for _, errors in form.errors.items():
                warning.extend(errors)
            flash(','.join(warning), 'warning')
        else:
            datum = form.get_data()
            datum['type'] = cur_type
            datum['status'] = 0
            datum['username'] = session['username']
            datum['timestamp'] = datetime.datetime.utcnow()
            datum['teacher_id'] = teacher_id
            # 写入数据库
            mongo_operator = MongoOperator(**MongoDB_CONFIG)
            result = mongo_operator.db['agent_feedback'].insert_one(datum)
            flash('操作成功，感谢您的反馈', 'success')

            return redirect_back()

    return render_template('scholar/feedback.html', form=form, cur_type=cur_type)


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
        # 查询数据库
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        condition = {'name': teacher_name}
        scope = {'title': 1, 'school': 1, 'institution': 1, 'name': 1, '_id': 0, 'id': 1}
        generator = mongo_operator.get_collection('basic_info').find(condition, scope)
        teachers = list(generator)

    return render_template('scholar/search.html', teachers=teachers, teacher_name=teacher_name)


@scholar_bp.route('/get_schools', methods=['GET'])
@login_required
def get_schools():
    """
    获取所有的学校的名称
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    scope = {'_id': 0, 'name': 1}
    generator = mongo_operator.get_collection('school').find({}, scope)

    schools = []
    for school in generator:
        schools.append(school['name'])

    return json.dumps(schools)


@scholar_bp.route('/get_institutions/<school>', methods=['GET'])
@login_required
def get_institutions(school):
    """
    根据学校的名称获取学院列表
    :param school:
    :return:
    """
    results = get_institutions_list(school)
    if results is False:
        results = []

    return json.dumps(results)


@scholar_bp.route('/get_teacher_id', methods=['POST'])
@login_required
def get_teacher_id():
    """
    根据教师的学校，学院，名字获取其id
    :param teacher_id:
    :return:
    """
    uid = session['uid']
    school = request.form.get("school")
    institution = request.form.get("institution")
    teacher = request.form.get("teacher")

    mongo = MongoOperator(**MongoDB_CONFIG)
    basic_info_col = mongo.get_collection("basic_info")
    outcome = basic_info_col.find_one({"name": teacher, "school": school, "institution": institution})

    if type(outcome) == None:
        return json.dumps({"success": False, "teacher_id": None})
    else:
        print(outcome)
        teacher_id = outcome["id"]

        print('--'*50, uid)
        print('--'*50, school, institution, teacher)
        print(teacher_id)
        return json.dumps({"success": True, "teacher_id": teacher_id})
