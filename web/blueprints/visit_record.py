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
    print("------------------------------", record_id)
    print("------------------------------", csrf_token)
    # mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # # 设置条件
    # condition = {"_id": ObjectId(record_id)}
    # mongo_operator.db['visit_record'].update_one(condition, {"$set":  {"status": 0}})

    return json.dumps({"success": True})
