from flask import Blueprint, render_template, session, request, redirect, url_for
from web.service.basic_info_service import search_teacher_basic_info
import json
import os

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
import datetime

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

    user_col = mongo_operator.get_collection("user")

    # 获取该商务所管辖的学校列表
    school_list = user_col.find_one({"id": uid})["charge_school"]

    school_col = mongo_operator.get_collection("school")

    school_institution = {}
    # 获取学校对应的学院列表，并组装成字典
    for school in school_list:
        institution_list = school_col.find_one({"name": school})["institutions"]
        school_institution[school] = institution_list

    print(school_institution)
    return render_template('personal.html', school=school_institution)


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
def visit_record():
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
    # TODO: 目前查询最多有一个查询该用户的日程安排
    result = mongo_operator.find_one({'user_id': uid}, 'visited_record')
    return render_template('visitRecode.html', visited_records=result['visited_record'])


@school_agent_bp.route('/visit_record/new', methods=['POST'])
@login_required
def new_visit_record():
    """
    插入新的拜访记录，当不存在拜访记录的时候会先新建
    :return:
    """
    # 获取当前的id
    record_id = request.form.get('id', type=int)
    record = {
        'id': record_id,
        'institution': request.form.get('institution'),
        'school': request.form.get('school'),
        'content': request.form.get('content'),
        'date': request.form.get('date'),
        'teacher': request.form.get('teacher'),
        'title': request.form.get('title'),
    }
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
    # 目前查询最多有一个查询该用户的日程安排
    result = mongo_operator.find_one({'user_id': uid}, 'visited_record')
    # 查询结果不存在，新建
    if result is None:
        record['id'] = 1
        mongo_operator.db['visited_record'].insert_one(
            {
                "user_id": uid,
                "max": 1,
                "visited_record": [record]
            })
    else:
        result['max'] += 1
        record['id'] = result['max']
        result['visited_record'].append(record)
        mongo_operator.db['visited_record'].update({'user_id': uid}, result)

    return json.dumps({'success': True})


@school_agent_bp.route('/visit_record/edit', methods=['POST'])
@login_required
def edit_visit_record():
    """
    修改拜访记录
    :return:
    """
    # 获取当前的id
    record_id = request.form.get('id', type=int)
    datum = {
        'institution': request.form.get('institution'),
        'school': request.form.get('school'),
        'content': request.form.get('content'),
        'date': request.form.get('date'),
        'teacher': request.form.get('teacher'),
        'title': request.form.get('title'),
        'id': record_id,
    }
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
    result = mongo_operator.find_one({'user_id': uid}, 'visited_record')
    i = 0
    for record in result['visited_record']:
        if record_id == record['id']:
            break
        i += 1
    result['visited_record'][i] = datum
    mongo_operator.db['visited_record'].update({'user_id': uid}, result)

    return json.dumps({'success': True})


@school_agent_bp.route('/visit_record/delete', methods=['POST'])
@login_required
def delete_visit_record():
    """
    删除拜访记录
    :return:
    """
    # 获取当前的id
    record_id = request.form.get('id', type=int)
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']
    result = mongo_operator.find_one({'user_id': uid}, 'visited_record')
    i = 0
    for record in result['visited_record']:
        if record_id == record['id']:
            break
        i += 1
    result['visited_record'].pop(i)
    mongo_operator.db['visited_record'].update({'user_id': uid}, result)

    return redirect(url_for('.visit_record'))


@school_agent_bp.route('/schedule')
@login_required
def schedule():
    """
    显示日程安排页面
    :return:
    """
    # 获取用户的id
    user_id = session['uid']
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 选定集合
    schedule_col = mongo_operator.get_collection("schedule")
    # 找到对应的user
    schedule_doc = schedule_col.find_one({"user_id": user_id})
    # 去除其下所有的日程（列表）
    schedule_list = schedule_doc["schedule"]

    # for per_schedule in schedule_list:
    #     print(per_schedule)
    return render_template("schedule.html", schedule_list=schedule_list)




@school_agent_bp.route('/info_modify',methods=['POST'])
@login_required
def info_modify():
    """
    进行信息修改
    :return:
    """
    info = {
        'title':request.form.get('title'),
        'type':request.form.get('type'),
        'target':request.form.get('target'),
        'content':request.form.get('content')
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


@school_agent_bp.route('/new_schedule', methods=['POST'])
@login_required
def new_schedule():
    """
    将用户新保存的拜访记录插入数据库
    :return:
    """
    # 获取用户的id,

    user_id = session['uid']

    remind_date = request.form.get('date')

    # 获取当前的日期，并组合成字符串

    current_day = datetime.datetime.now().date()

    # current_date = str(current_year) + "-" + str(current_month) + "-" + str(current_day)
    current_date = str(current_day)

    # 前端所保存的提醒时间、日程内容、以及是否完成
    # remind_date = "2019-7-30"

    schedule_content = "拜访罗军舟"

    is_completed = False

    mongo_operator = MongoOperator(**MongoDB_CONFIG)

    schedule_col = mongo_operator.get_collection("schedule")
    # 获取数据库中对应该user_id的文档
    schedule_doc = schedule_col.find_one({"user_id": user_id})
    # 获取数据库中的计划列表
    schedule_list = schedule_doc["schedule"]
    # 计算新的schedule_id
    new_schedule_id = len(schedule_list) + 1

    store_dict = {
        "schedule_id": new_schedule_id,
        "create_date": current_date,
        "content": schedule_content,
        "remind_date": remind_date,
        "is_completed": str(is_completed)
    }
    # 更新计划列表
    schedule_list.append(store_dict)
    # 更新集合
    schedule_col.update({"user_id": user_id}, {"$set": {"schedule": schedule_list}})




@school_agent_bp.route('', methods=['POST'])
@login_required
def edit_schedule():
    """
    用户编辑schedule
    :return:
    """

    uid = session["id"]
    # TODO 获取修改后的时间以及内容,没做完

    edit_date = request.form.get('date')
    edit_content = request.form.get('content')
    edit_is_completed = str(request.form.get('is_completed'))

    print("0-----------------")
    print(edit_date)
    print(edit_content)
    print(edit_is_completed)
    # TODO 如何获取schedule_id
    schedule_id = 1

    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取schedule集合
    schedule_col = mongo_operator.get_collection("schedule")
    # 获取集合中的schedule列表
    schedule_list = schedule_col.find_one({"user_id": uid})["schedule"]
    # 查找对应的schedule_id
    for schedule in schedule_list:
        if schedule["schedule_id"] == schedule_id:
            schedule["content"] = edit_content
            schedule["remind_date"] = edit_date
            schedule["is_completed"] = edit_is_completed
            print("-----------已更新")
            break

    # 更新schedule_list
    schedule_col.update({"user_id": uid}, {"$set": {"schedule": schedule_list}})


def set_whether_completed_or_canceled(user_id, schedule_id, type):
    """
    设置该用户下的该计划是否完成或取消

    :param user_id:
    :param schedule_id:
    :param type: ==0 表示未完成， ==1 表示已完成 ==-1表示该计划已经取消
    :return: 返回true表示修改成功，否则失败
    """

    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取schedule集合
    schedule_col = mongo_operator.get_collection("schedule")
    # 获取集合中的schedule列表
    schedule_list = schedule_col.find_one({"user_id": user_id})["schedule"]
    # 查找对应的schedule_id
    res = False
    for schedule in schedule_list:
        if schedule["schedule_id"] == schedule_id:
            schedule["is_completed"] = str(type)
            print("-----------已更新")
            res = True
            break

    # 更新schedule_list
    schedule_col.update({"user_id": user_id}, {"$set": {"schedule": schedule_list}})

    return res

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

        # TODO 从数据库中获取当前用户与这些人的关系，合并到 relation_data 中

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


# if __name__ == '__main__':
#     # scholar_info(73927)
#     # print(get_relations("北京大学", "化学生物学与生物技术学院"))
#     # new_schedule()
#     # index()
#     # edit_schedule()
#     # set_whether_completed(100006,1,1)
#     pass