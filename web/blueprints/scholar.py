from flask import Blueprint, render_template, request, flash
from flask_login import current_user
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


@scholar_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
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
            datum['username'] = current_user.name
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
    print("----------获取教师id------------------")
    uid = session['uid']
    school = request.form.get("school")
    institution = request.form.get("institution")
    teacher = request.form.get("teacher")

    print("teacher   ", teacher)

    mongo = MongoOperator(**MongoDB_CONFIG)
    basic_info_col = mongo.get_collection("basic_info")
    outcome = basic_info_col.find_one({"name": teacher, "school": school, "institution": institution})

    if outcome == None:
        print("---------未找到此人")
        return json.dumps({"success": False, "teacher_id": None})
    else:
        print(outcome)
        teacher_id = outcome["id"]

        print('--'*50, uid)
        print('--'*50, school, institution, teacher)
        print(teacher_id)
        # 将用户和教师新增的关系入库
        add_relation(teacher_id, uid)

    return json.dumps({"success": True, "teacher_id": teacher_id})


def add_relation(teacher_id, uid):
    """
    将新建的拜访记录的用户与教师的关系存入数据库
    :param teacher_id:
    :param uid:
    :return:
    """
    print("-----------------------add_relation-------------------------------")
    print(teacher_id)
    mongo = MongoOperator(**MongoDB_CONFIG)
    # 获取教师基本信息集合
    basic_info_col = mongo.get_collection("basic_info")
    # 获取用户的集合
    user_col = mongo.get_collection("user")
    # 获取对应用户的文档
    user_doc = user_col.find_one({"id": uid, "related_teacher": {"$elemMatch": {"id": teacher_id}}}, {"related_teacher": 1, "_id": 0})
    if user_doc is None:
        # print("---")
        user_doc = user_col.find_one({"id": uid}, {"related_teacher": 1, "_id": 0})
        name = basic_info_col.find_one({"id": teacher_id}, {"name": 1, "_id": 0})["name"]
        teacher_list = user_doc["related_teacher"]
        teacher_list.append({
            "id": teacher_id,
            "name": name,
            "weight": 1
        })
        user_col.update({"id": uid}, {"$set": {"related_teacher": teacher_list}})

    else:
        for d in user_doc["related_teacher"]:
            if d["id"] == teacher_id:
                w = d["weight"]
                d["weight"] = w+1
                break
        user_col.update({"id": uid}, {"$set": {"related_teacher": user_doc["related_teacher"]}})

    # print(user_col.find_one({"id": uid, "related_teacher": {"$elemMatch": {"id": teacher_id}}}, {"related_teacher": 1, "_id": 0}))

