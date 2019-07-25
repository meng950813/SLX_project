from flask import Blueprint, render_template, request
from bson.objectid import ObjectId
import json
from flask_login import current_user
import threading
import datetime

from web.blueprints.auth import login_required
from web.config import MongoDB_CONFIG, NEO4J_CONFIG
from web.utils.mongo_operator import MongoOperator
from web.utils.neo4j_operator import NeoOperator


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
                {"_id": 0, 'paper_id': 0, 'patent_id': 0, 'funds_id': 0, 'honor': 0, 'edu_exp': 0, 'birth_year': 0, 'other_title': 0}
            )
        if teacher_info is None:
            return json.dumps({'success': False, "message": "教师不存在,请检查输入的信息"})

        # 插入拜访记录
        result = mongo_operator.get_collection('visit_record').insert_one(record)
        # 是否存在完善的信息
        external_info = {'type': 'modify', 'status': 1, 'username': current_user.name, 'timestamp': datetime.datetime.utcnow()}
        modifying = False
        external_keys = [
            ('position', 'position'), ('teacher-title', 'title'), ('telephone', 'phone_number')
            , ('email', 'email'), ('office-phone', 'office_number'), ('department', 'department')]
        for key in external_keys:
            whole_key = 'basic_info[%s]' % key[0]
            if whole_key in request.form:
                modifying = True
                external_info[key[1]] = request.form[whole_key]
        # 更新老师信息 并写入到反馈中
        if modifying:
            teacher_info.update(external_info)
            # 写入数据库
            mongo_operator.db['agent_feedback'].insert_one(teacher_info)

        # 多线程执行插入用户与教师的关系
        threading.Thread(target=upsert_relation_of_visited, args=(uid, teacher_info['id'], teacher_info['name'])).start()
        # upsert_relation_of_visited(uid, teacher_info['id'], teacher_info['name'])

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


def upsert_relation_of_visited(user_id, teacher_id, teacher_name):
    """
    by chen
    在图数据库中添加拜访关系
    添加拜访信息到 mongoDB 的user 表中
    :param user_id:
    :param teacher_id:
    :param teacher_name:
    :return: None
    """
    # 操作neo4j
    try:
        # back ==> {success: True / False, message:xxxx}
        back = NeoOperator(**NEO4J_CONFIG).upsert_agent_relation(user_id, teacher_id)
        if not back['success']:
            print("更新拜访记录到图数据库失败，原因：%s" % back['message'])

    except Exception as e:
        print("更新拜访记录到图数据库失败，原因：%s" % e)

    # TODO 后期剔除该部分
    # 操作mongo
    try:
        collection_user = MongoOperator(**MongoDB_CONFIG).get_collection("user")
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
        print("更新拜访记录到mongo失败, 原因：%s" % e)


if __name__ == '__main__':
    upsert_relation_of_visited(100000, 135495, "张三")
    upsert_relation_of_visited(100000, 162702, "")