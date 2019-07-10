from flask import Blueprint, render_template, session, request, redirect, url_for
from web.service.basic_info_service import search_teacher_basic_info
import json
import os
from bson.objectid import ObjectId

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
import datetime
from bson.objectid import ObjectId

school_agent_bp = Blueprint('school_agent', __name__)


@school_agent_bp.route('/')
@school_agent_bp.route('/homepage')
@login_required
def index():
    """
    学校商务的个人主页
    :return:
    """

    # TODO 获取当前商务负责的学校 / 学院及其建立的关系
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']

    # 获取该商务的信息
    user_result = mongo_operator.find_one({"id": uid}, "user")
    # 获取负责的学校名称列表
    schools = user_result['charge_school']
    # 仅仅获取第一个学校的学院数组
    collection = mongo_operator.get_collection("school")
    school_result = collection.find_one({"name": schools[0]})
    institutions = school_result['institutions']

    return render_template('personal.html', schools=schools, institutions=institutions)


@school_agent_bp.route('/scholar/<int:teacher_id>')
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

    return render_template('detail.html', teacher_basic_info=teacher_basic_info, length=length)


@school_agent_bp.route('/visit_record')
@login_required
def manage_visit_record():
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
    # 查询询该用户的日程安排
    generator = mongo_operator.find({'user_id': uid, 'status': 1}, 'visit_record')
    return render_template('visit_record.html', visited_records=list(generator))


@school_agent_bp.route('/visit_record/new', methods=['POST'])
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


@school_agent_bp.route('/visit_record/edit', methods=['POST'])
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


@school_agent_bp.route('/visit_record/delete', methods=['POST'])
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
    condition = {"_id": ObjectId(record_id)}
    mongo_operator.db['visit_record'].update_one(condition, {"$set":  {"status": 0}})

    return json.dumps({"success": True})


@school_agent_bp.route('/info_modify', methods=['POST'])
@login_required
def info_modify():
    """
    进行信息修改

    :return:
    """
    info = {
        'title': request.form.get('title'),
        'type': request.form.get('type'),
        'target': request.form.get('target'),
        'content': request.form.get('content')
    }
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
    mongo_operator.db['info_modify'].insert_one(
        {
            "user_id": uid,
            "info_modify": info
        })
    return json.dumps({'success': True})


@school_agent_bp.route('/schedule')
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
    schedule_list = schedule_col.find({"user_id": user_id, "status": 0}).sort([("remind_date", -1)])

    # print(schedule_list)

    return render_template("schedule.html", schedule_list=schedule_list)


@school_agent_bp.route('/edit_schedule', methods=['POST'])
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


@school_agent_bp.route('/operate_schedule', methods=['POST'])
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


@school_agent_bp.route('/info_reminder')
@login_required
def info_reminder():
    """
    进入消息提醒页面
    :return:
    """
    session['info_num'] = ""
    return render_template("info_reminder.html")


def get_relations(school, institution):
    """
    获取当前用户与某一学院之中的人员关系及其中的内部社区分布
    :param school: 学校名
    :param institution:学院名
    :return: 可供echarts直接渲染的json文件 or False
    """
    file_path = "../static/relation_data/%s%s.txt" % (school, institution)

    # 判断该学院社区网络文件是否存在
    if not os.path.exists(file_path):
        print("%s %s 的社交网络尚未生成！" % (school, institution))
        return False
    with open(file_path, "r") as f:
        data = json.loads(f.read())
        print(data)
        print(type(data))
        relation_data = format_relation_data(data)

        # TODOrelation_data 中

        return json.dumps(relation_data)


def format_relation_data(data):
    """
    将关系数据简化为可发送的数据
    :param data: 预处理过的社区网络数据
    :return: 可供echarts直接渲染的json文件 or False
    """
    try:
        """
            nodes 中舍弃 code, school, insititution, centrality, class 属性, 
            添加 label,symbolSize 属性
        """
        for node in data["nodes"]:
            node['label'], node['name'] = node['name'], str(node['teacherId'])
            node['category'], node["draggable"] = node['class'] - 1, True
            node['symbolSize'] = (node['centrality'] * 30 + 5)

            # 核心节点
            if node['teacherId'] in data["core_node"]:
                node["itemStyle"] = {
                    "normal": {
                        "borderColor": 'yellow',
                        "borderWidth": 5,
                        "shadowBlur": 10,
                        "shadowColor": 'rgba(0, 0, 0, 0.3)'
                    }
                }
            del node["teacherId"], node["class"], node["centrality"], node["code"], node["school"], node["insititution"]

        data["links"] = []
        for link in data["edges"]:
            if "source" not in link or "target" not in link:
                print("此关系缺少 起点 / 终点：", link)
            else:
                link["source"], link["target"] = str(link["source"]), str(link["target"])
                link["value"] = link["weight"]
                del link['weight']
                data["links"].append(link)

        data["community"] = []
        for cate in data["community_data"]:
            data["community"].append(int(list(cate.keys())[0]) - 1)

        del data["community_data"], data["algorithm_compare"], data["core_node"], data["edges"]

        return data

    except Exception as e:
        print(e)
        return False


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
    

    try:
        # 更新schedule_list
        result = schedule_col.update_one({"_id": ObjectId(schedule_id)},{"$set": {"status": status}})
        return result.modified_count
    except Exception as e:
        print("schedule_id 不符合标准", e)
        return 0


if __name__ == '__main__':
    # scholar_info(73927)
    # print(get_relations("北京大学", "化学生物学与生物技术学院"))
    # new_schedule()
    # index()
    # edit_schedule()
    # set_whether_completed(100006,1,1)
    # pass
    # print(set_whether_completed_or_canceled(100006, 0, 1))
    # print(set_whether_completed_or_canceled(100001, 1, 1))
    # print(set_whether_completed_or_canceled(100006, 1, -1))
    data = {
        "create_date": "2019-06-08",
        "content": "测试插入函数的数据",
        "remind_date": "2019-08-06",
        "status": 0
    }
    # print(insert_or_edit_schedule(data, 100001))


