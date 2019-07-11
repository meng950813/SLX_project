from flask import Blueprint, render_template, session, request
import json

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
import datetime
from bson.objectid import ObjectId


schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/schedule')
@login_required
def schedule():
    """
    显示日程安排页面
    :return:
    """

    print("------------------------显示日程安排的页面------------------------------")
    # 获取用户的id
    user_id = session['uid']

    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 选定集合
    schedule_col = mongo_operator.get_collection("schedule")
    # 找到对应的user ,根据提醒日期对日程进行降序排序
    schedule_list = schedule_col.find({"user_id": user_id, "status": 0}).sort([("remind_date", 1)])

    # print(schedule_list)

    return render_template("schedule.html", schedule_list=schedule_list)


@schedule_bp.route('/edit_schedule', methods=['POST'])
@login_required
def edit_schedule():
    """
    创建新的日程安排或编辑已有的日程
    :return:
    """

    schedule_id = request.form.get('id')
    data = {
        # 获取用户的id,
        "user_id": session['uid'],
        # 获取当前的日期，并组合成字符串
        "create_date": str(datetime.datetime.now().date()),
        # 详细内容
        "content": request.form.get("content"),
        "remind_date": request.form.get('date'),
        # 标识当前日程的状态: 0 => 未处理; 1 => 已完成; -1 => 已舍弃
        "status": 0
    }

    back = insert_or_edit_schedule(data, schedule_id)
    if back:
        return json.dumps({"success": True, "message": "操作成功"})

    return json.dumps({"success": False, "message": "操作失败, code: %s" % back})


@schedule_bp.route('/operate_schedule', methods=['POST'])
@login_required
def operate_schedule():
    """
    标记当前日程 已取消 or 已完成
    :return:
    """
    schedule_id = request.form.get('id')
    status = request.form.get('type', type=int)

    back = set_whether_completed_or_canceled(schedule_id, status)

    if back:
        return json.dumps({"success": True, "message": "操作成功"})

    return json.dumps({"success": False, "message": "操作失败, code: %s" % back})


def insert_or_edit_schedule(data, schedule_id):
    """
    根据 schedule_id 决定 插入/更新 日程数据
    :param data: 具体数据
    :param schedule_id: string 类型的objectId
    :return: 0 / 1 or objectId
    """
    schedule_col = MongoOperator(**MongoDB_CONFIG).get_collection("schedule")

    try:
        # 合法objectId ==> 修改
        obj_id = ObjectId(schedule_id)
        result = schedule_col.update_one({'_id': obj_id}, {"$set": data})
        return result.modified_count

    # TODO to checkout error type
    except Exception as t:
        # 非法objectId ==> 创建
        print("type error", type(t), t)
        result = schedule_col.insert_one(data)
        return result.inserted_id

    except Exception as e:
        print("添加/修改错误 ", e, schedule_id)
        return 0


def set_whether_completed_or_canceled(schedule_id, status):
    """
    设置该用户下的该计划是否完成或取消
    :param schedule_id:
    :param status: ==0 表示未完成， ==1 表示已完成 ==-1表示该计划已经取消
    :return: 返回true表示修改成功，否则失败
    """

    schedule_col = MongoOperator(**MongoDB_CONFIG).get_collection("schedule")

    status = 1 if status == 1 else -1
    
    try:
        # 更新schedule_list
        result = schedule_col.update_one({"_id": ObjectId(schedule_id)},{"$set": {"status": status}})
        # print(result.modified_count, result.matched_count)
        # print(result)
        return result.modified_count
    except Exception as e:
        print("schedule_id 不符合标准", e)
        return 0

if __name__ == "__main__":
    # print(set_whether_completed_or_canceled(100006, 0, 1))
    # print(set_whether_completed_or_canceled(100001, 1, 1))
    # print(set_whether_completed_or_canceled(100006, 1, -1))
    data = {
        "create_date": "2019-06-08",
        "content": "测试插入函数的数据",
        "remind_date": "2019-08-06",
        "status": 0
    }
    a = insert_or_edit_schedule(data, 100001)
    print(a, type(a))
    b = str(a)
    print(b, type(b))
