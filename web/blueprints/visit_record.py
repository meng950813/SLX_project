from flask import Blueprint, render_template, request
from bson.objectid import ObjectId
import json
from flask_login import current_user

from web.blueprints.auth import login_required
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


visit_record_bp = Blueprint('visit_record', __name__)


@visit_record_bp.route('/visit_record')
@login_required
def manage_visit_record():
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = current_user.id
    # 查询询该用户的日程安排
    generator = mongo_operator.find({'user_id': uid, 'status': 1}, 'visit_record')
    return render_template('visit_record.html', visited_records=list(generator))


@visit_record_bp.route('/visit_record/new', methods=['POST'])
@login_required
def new_visit_record():
    """
    插入新的拜访记录
    :return:
    """
    # 获取用户的uid

    uid = current_user.id
    record = {
        'institution': request.form.get('institution'),
        'school': request.form.get('school'),
        'content': request.form.get('content'),
        'date': request.form.get('date'),
        'teacher': request.form.get('teacher'),
        'title': request.form.get('title'),
        "user_id": uid,
        "status": 1,
    }
    teacher_id = request.form.get("teacher_id")
    # print(id)
    if teacher_id is None:
        print("-------------未插入")
        return json.dumps({'success': False, 'record_id': str("")})

    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取拜访记录集合
    collection = mongo_operator.get_collection("visit_record")
    print("-----------------已插入")
    result = collection.insert_one(record)
    record_id = result.inserted_id

    print("new visit record---------------------------")
    print(teacher_id)

    return json.dumps({'success': True, 'record_id': str(record_id)})


@visit_record_bp.route('/visit_record/edit', methods=['POST'])
@login_required
def edit_visit_record():
    """
    修改拜访记录
    :return:
    """
    print("---------------修改拜访记录-----------------")
    # 获取当前的id
    record_id = request.form.get('id')
    datum = {
        'institution': request.form.get('institution'),
        'school': request.form.get('school'),
        'content': request.form.get('content'),
        'date': request.form.get('date'),
        'teacher': request.form.get('teacher'),
        'title': request.form.get('title'),
    }

    teacher_id = request.form.get("teacher_id")
    # print(id)
    print("teacher_id", teacher_id)
    print(type(teacher_id))
    if teacher_id is None or teacher_id is '':
        print("-------------未修改")
        return json.dumps({'success': False})
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 更新
    condition = {"_id": ObjectId(record_id)}
    result = mongo_operator.db['visit_record'].update_one(condition, {"$set":  datum})
    print("--------已修改")
    return json.dumps({'success': True})


@visit_record_bp.route('/visit_record/delete', methods=['POST'])
@login_required
def delete_visit_record():
    """
    删除拜访记录
    :return:
    """
    # 获取当前的id
    print("----------------------------准备删除拜访记录-------------------------")
    record_id = request.form.get('id')
    csrf_token = request.form.get('csrf_token')
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 设置条件
    condition = {"_id": ObjectId(record_id)}
    mongo_operator.db['visit_record'].update_one(condition, {"$set":  {"status": 0}})

    return json.dumps({"success": True})


@visit_record_bp.route('/get_teacher_id', methods=['POST'])
@login_required
def get_teacher_id():
    """
    根据教师的学校，学院，名字获取其id
    :param teacher_id:
    :return:
    """
    print("----------获取教师id------------------")
    uid = current_user.id
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

