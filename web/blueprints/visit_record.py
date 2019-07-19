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
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    try:
        # back => dict or None
        teacher_info = mongo_operator.get_collection("basic_info").find_one(
                {"name": record['teacher'], "school": record['school'], "institution": record['institution']},
                {"_id": 1, "id": 1, "name": 1}
            )
        if teacher_info is None:
            return json.dumps({'success': False, "message": "教师不存在,请检查输入的信息"})

        # 插入拜访记录
        result = mongo_operator.get_collection("visit_record").insert_one(record)
        
        # TODO 多线程执行插入用户与教师的关系
        upsert_relation_of_visited(uid, teacher_info['id'], teacher_info['name'])

        return json.dumps({'success': True, 'record_id': str(result.inserted_id)})

    except Exception as e:
        print("插入新拜访记录出错，原因：%s" % e)
        return json.dumps({'success': False, "message": "插入失败, 请确认数据是否正确"})


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
        'content': request.form.get('content'),
        'date': request.form.get('date'),
        'title': request.form.get('title'),
    }
    try:
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        # 更新
        condition = {"_id": ObjectId(record_id)}
        result = mongo_operator.db['visit_record'].update_one(condition, {"$set":  datum})

        if result.matched_count > 0:
            return json.dumps({'success': True})
        else:
            return json.dumps({"success": False, "message": "修改失败，请稍后再试"})
    except Exception as e:
        print("修改拜访记录出错，原因：%s" % e)
        return json.dumps({'success': False, "message": "修改失败"})


@visit_record_bp.route('/visit_record/delete', methods=['POST'])
@login_required
def delete_visit_record():
    """
    删除拜访记录
    :return:
    """
    # 获取当前的id
    record_id = request.form.get('id')
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 设置条件
    try:
        condition = {"_id": ObjectId(record_id)}
        result = mongo_operator.db['visit_record'].update_one(condition, {"$set":  {"status": 0}})
        if result.matched_count > 0:
            return json.dumps({'success': True})
        else:
            return json.dumps({'success': False, "message": "删除失败"})

    except Exception as e:
        print("删除拜访记录失败，原因：%s" % e)
        return json.dumps({'success': False, "message": "删除失败"})


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

def upsert_relation_of_visited(user_id, teacher_id, teacher_name):
    """
    添加拜访信息到 user 表中
    :param user_id:
    :param teacher_id:
    :param teacher_name:
    :return:
    """
    collection_user = MongoOperator(**MongoDB_CONFIG).get_collection("user")
    try:
        # back => None or dict{"_id":ObjectId("xxx"), "related_teacher":[{id:xx, name, visited_count:12, acitve_count: 123}]}
        visited_record = collection_user.find_one({"id": user_id, "related_teacher.id": teacher_id}, {"related_teacher.$": 1})

        if visited_record:
            info = visited_record['related_teacher'][0]
            count = int(info['visited_count'] + 1)
            collection_user.update_one({"_id": visited_record["_id"], "related_teacher.id": teacher_id},
                                       {"$set": {"related_teacher.$.visited_count": count}})
        else:
            insert_data = {
                "id": teacher_id,
                "name": teacher_name,
                "visited_count": int(1),
                "acitve_count": int(0)
            }
            collection_user.update_one({"id": user_id}, {"$set": {"related_teacher": [insert_data]}})

    except Exception as e:
        print("更新关系失败, 原因：%s" % e)


if __name__ == '__main__':
    upsert_relation_of_visited(100003, 135495, "张三")