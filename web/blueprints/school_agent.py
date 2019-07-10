from flask import Blueprint, render_template, session, request
from web.service.basic_info_service import search_teacher_basic_info
import json
import os

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG

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


