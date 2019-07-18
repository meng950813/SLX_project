from flask import Blueprint, render_template, request
from flask_login import current_user
from datetime import datetime
import json

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG


reminder_bp = Blueprint("reminder", __name__)


@reminder_bp.route('/info_reminder')
@login_required
def info_reminder():
    """
    进入消息提醒页面
    :return:
    """
    uid = current_user.id

    # 获取发送给该用户的所有信息
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    collection = mongo_operator.get_collection('message')
    messages = collection.find({"to_id": uid}).sort([('date', -1)])
    unchecked_message = []
    checked_message = []

    # 把信息分为已读和未读
    for message in messages:
        if message['state'] == 1:
            checked_message.append(message)
        else:
            unchecked_message.append(message)

    # 标记未读的为已读
    collection = mongo_operator.get_collection("message")
    collection.update_many({"to_id": uid}, {"$set": {"state": 1}})

    return render_template("info_reminder.html",
                           checked_message=checked_message, unchecked_message=unchecked_message)


@reminder_bp.route('/add_message', methods=['POST'])
@login_required
def insert_message():
    state = 0
    date = datetime.utcnow()
    # 发送者
    from_id = current_user.id
    from_name = current_user.name
    # 接受者
    receiver = request.form.get("receiver")
    receiver_id = request.form.get('receiver_id', type=int)
    detail = request.form.get("content")

    message = {
        'state': state,
        'date': date,
        'from_id': from_id,
        'from_name': from_name,
        'to_id': receiver_id,
        'to_name': receiver,
        'detail': detail
    }
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    collection = mongo_operator.get_collection("message")
    collection.insert_one(message)

    return json.dumps({"success": True, "message": "操作成功"})


@reminder_bp.route('/get_agents')
def get_agents():
    """
    获取所有的用户，并返回一个字典数组{name,id}
    :return:
    """
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    collection = mongo_operator.get_collection("user")
    # 仅仅需要id和name
    results = collection.find({}, {"name": 1, "id": 1, "_id": 0})
    users = list(results)

    return json.dumps(users, ensure_ascii=False)

