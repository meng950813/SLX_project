from flask import Blueprint, session, render_template, request
from bson.objectid import ObjectId
import json

from web.blueprints.auth import login_required
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


visit_record_bp = Blueprint('visit_record', __name__)


@visit_record_bp.route('/visit_record')
@login_required
def manage_visit_record():
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
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
    uid = session['uid']
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
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取拜访记录集合
    collection = mongo_operator.get_collection("visit_record")
    result = collection.insert_one(record)
    record_id = result.inserted_id


    # 新增用户教师之间的关系
    teacher_id = request.form.get("teacher_id")
    add_relation(teacher_id, uid)

    return json.dumps({'success': True, 'record_id': str(record_id)})


@visit_record_bp.route('/visit_record/edit', methods=['POST'])
@login_required
def edit_visit_record():
    """
    修改拜访记录
    :return:
    """
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
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 更新
    condition = {"_id": ObjectId(record_id)}
    result = mongo_operator.db['visit_record'].update_one(condition, {"$set":  datum})

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


def add_relation(teacher_id, uid):
    """
    将新建的拜访记录的用户与教师的关系存入数据库
    :param teacher_id:
    :param uid:
    :return:
    """
    print("-----------------------add_relation-------------------------------")
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
        print(user_doc)
        name = basic_info_col.find_one({"id": teacher_id}, {"name": 1, "_id": 0})
        teacher_list = user_doc["related_teacher"]
        teacher_list.append({
            "id": teacher_id,
            "name": name,
            "weight": 1
        })
        print(teacher_list)
        user_col.update({"id": uid}, {"$set": {"related_teacher": teacher_list}})

    else:
        print(type(user_doc))
        for d in user_doc["related_teacher"]:
            if d["id"] == teacher_id:
                w = d["weight"]
                d["weight"] = w+1
                break
        user_col.update({"id": uid}, {"$set": {"related_teacher": user_doc["related_teacher"]}})
        print(user_doc)

    print(user_col.find_one({"id": uid, "related_teacher": {"$elemMatch": {"id": teacher_id}}}, {"related_teacher": 1, "_id": 0}))

if __name__ == '__main__':
    add_relation(73927, 100003)




