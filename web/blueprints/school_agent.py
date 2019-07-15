from flask import Blueprint, render_template, session, request
import json
import os

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
from web.settings import basedir

school_agent_bp = Blueprint('school_agent', __name__)


@school_agent_bp.route('/')
@school_agent_bp.route('/homepage')
@login_required
def index():
    """
    学校商务的个人主页
    :return:
    """
    # 获取当前商务负责的学校 / 学院及其建立的关系
    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 获取用户的uid
    uid = session['uid']

    if "charge_school" in session:
        user_info = {
            'charge_school': session['charge_school'],
            "related_teacher": session['related_teacher']
        }
    else:
        # 获取该商务的信息
        user_info = mongo_operator.get_collection("user").find_one({"id": uid})

        if not ("related_teacher" in user_info):
            user_info["related_teacher"] = None

        if not ("charge_school" in user_info):
            user_info["charge_school"] = None

        session["charge_school"] = user_info['charge_school']
        session["related_teacher"] = user_info["related_teacher"]

    schools = user_info['charge_school']

    if schools:
        # 仅仅获取第一个学校的学院数组
        institutions = get_institution(schools[0])

        return render_template('personal.html', schools=schools, institutions=institutions)
    else:
        return render_template('personal.html', schools=[], institutions=[])


@school_agent_bp.route('/change_school', methods=["GET"])
@login_required
def change_school():
    school = request.args.get("school")
    institutions = get_institution(school)
    if institutions:
        return json.dumps(institutions)
    return json.dumps({"success": False, "message": "学校名有误"})


@school_agent_bp.route('/change_institution', methods=["GET"])
@login_required
def change_institution():
    school = request.args.get("school")
    institution = request.args.get("institution")
    # print(school, institution)

    if not ("related_teacher" in session):
        return json.dumps({"success": False, "message": "请登陆"})

    json_data = get_relations(school, institution, session.get("related_teacher"))

    if json_data:
        return json_data
    else:
        return json.dumps({"success": False, "message": "暂无当前学院的社交网络数据"})


def get_institution(school):
    """
    获取学校所有的学院信息，按 visited 排序
    :param school: str 学校名
    :return: [xxx,xxx,xxx...] or False
    """
    back = MongoOperator(**MongoDB_CONFIG).get_collection("school").find_one({"name": school}, {"institutions": 1})
    if not back or not ("institutions" in back):
        return False

    institutions = back['institutions']
    # 按照学院被点击次数排序 ==> [{"visited":xx, "name":xx}, ...]
    institutions.sort(key=lambda k: k.get("visited"), reverse=True)
    # 取出学院名，转为list
    return [item["name"] for item in institutions]


def get_relations(school, institution, agent_relation):
    """
    获取当前用户与某一学院之中的人员关系及其中的内部社区分布
    :param school: 学校名
    :param institution: 学院名
    :param agent_relation: 商务自己建立的联系, [{id:xxx, name: xxx, weight: 123},{...},....]
    :return: 可供echarts直接渲染的json文件 or False
    """
    # TODO: by xiaoniu 由于部署问题，该路径可能需要修改
    file_path = os.path.join(basedir, 'static', 'relation_data', '%s%s.txt' % (school, institution))

    # 判断该学院社区网络文件是否存在
    if not os.path.exists(file_path):
        # print(file_path)
        # print(os.path.exists(file_path))
        print("%s %s 的社交网络尚未生成！" % (school, institution))
        return False
    with open(file_path, "r") as f:
        data = json.loads(f.read())
        # print(data)
        # print("in get_relations, already open file")
        relation_data = format_relation_data(data, agent_relation)
        return json.dumps(relation_data)


def format_relation_data(data, agent_relation):
    """
    将关系数据简化为可发送的数据
    :param data: 预处理过的社区网络数据
    :param agent_relation: 商务的社交数据
    :return: 可供echarts直接渲染的json文件 or False
    """
    try:
        """
            nodes 中舍弃 code, school, insititution, centrality, class 属性, 
            添加 label,symbolSize 属性
            class 属性是指节点所属社区，从 1 开始
        """
        teacher_id_dict = dict()
        class_id_dict = dict()

        for node in data["nodes"]:
            node['label'], node['name'] = node['name'], str(node['teacherId'])
            node['category'], node["draggable"] = node['class'], True
            node['symbolSize'] = int(node['centrality'] * 30 + 5)

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

                # 保存 class 的种类是为了划分社区 ==> 实现这一功能的前提是 class 值不存在断档
                # 其值为该社区核心节点 id
                class_id_dict[node["class"]] = node["teacherId"]

            # 保存 teacherId => 判定商务创建的所有关系中有哪些属于当前社区;
            # 以其 class 为值是为了更方便的在隐藏非核心节点时, 将商务与其的关系累加到核心节点上
            teacher_id_dict[node['teacherId']] = node["class"]

            del node["teacherId"], node["class"], node["centrality"], node["code"], node["school"], node["insititution"]

        data["links"] = []
        for link in data["edges"]:
            if "source" not in link or "target" not in link:
                print("缺少 起点 / 终点：", link)
            else:
                link["source"], link["target"] = str(link["source"]), str(link["target"])
                link["value"] = link["weight"]
                del link['weight']
                data["links"].append(link)

        """
            在生成的社区关系文件中, community_data 中的数据应该是每个社区中的对比数据, 即其 key 应当包含每个class的值
            但有部分数据并非如此, community_data 的 key 并未包括所有 class, 因此不能使用其作为分类的标准
            
            前提: nodes中的class连续 ==> 不会出现 1,2,5,...的情况
            传递社区总数
        """
        data["community"] = len(class_id_dict)

        # data["community"] = [0]
        # for cate in data["community_data"]:
        #     data["community"].append(int(list(cate.keys())[0]))

        # 添加商务节点
        data["nodes"].append(create_agent_node())

        # 添加商务创建的社交关系
        if agent_relation:
            agent_relation_data = create_agent_relation(agent_relation, teacher_id_dict, class_id_dict)

            data["links"].extend(agent_relation_data[0])

            data["core_node"] = agent_relation_data[1]

        del data["community_data"], data["algorithm_compare"], data["edges"]

        return data

    except Exception as e:
        print(e)
        return False


def create_agent_node():
    """
    创建商务的节点
    :return: dict {"":}
    """
    return {
        "name": "0",
        "label": "我",
        "category": 0,
        # 'circle', 'rect', 'roundRect', 'triangle', 'diamond', 'pin', 'arrow', 'none'
        "symbol": "diamond",
        "draggable": True,
        "symbolSize": 36,
        "itemStyle": {
            "normal": {
                "borderColor": 'white',
                "borderWidth": 2,
                "shadowBlur": 6,
                "shadowColor": 'rgba(0, 0, 0, 0.3)'
            }
        }
    }


def create_agent_relation(data, teacher_dict, class_dict):
    """
    创建商务与当前学院中老师的关系
    :param data: 商务创建的所有联系, [{id:xxx, name: xxx, weight: 123},{...},....]
    :param teacher_dict: dict 当前学院的教师id列表, 值为其所属社区号
    :param class_dict: dict 当前学院中的社区号, 值为其中核心节点的 teacherId
    :return: tuple (
            [{source:"0",target:"xxx",normal:{lineStyle:{width:...}}}],
            {"core_node_teacherId": totalWeight}
        )
    """
    back = []

    # 用于保存商务与该社区所有老师的关系之和
    # 格式为: {"core_node_teacherId": totalWeight}
    core_node = {}

    for item in data:
        if not item.get("id") in teacher_dict:
            continue

        if not ("weight" in item):
            item["weight"] = 1

        info = {
            "source": "0",
            "target": str(item['id']),
            "visited": item['weight'],
            "lineStyle": {
                "normal": {
                    # TODO 根据拜访次数设定连线宽度
                    "width": 5
                }
            }
        }
        back.append(info)

        try:
            # 防止取不到值
            core_teacher = class_dict[teacher_dict[item['id']]]
            if core_teacher in core_node:
                core_node[core_teacher] += item["weight"]
            else:
                core_node[core_teacher] = item["weight"]
        except Exception as e:
            print("取不到正确的值")
            print(e)

    return back, core_node


def create_agent_relation_with_core_node(core_node):
    """
    创建商务与每个社区核心节点的关系, 该关系为商务与该社区中非核心节点关系的总和
    :param core_node: dict 商务与核心节点的关系权重, 格式为: {"teacherId": weight, ...}
    :return: list [{source:"0",target:"xxx", "core": True, normal:{lineStyle:{width:...}}}]
    """
    back = []
    for teacherId, weight in core_node.items():
        back.append({
            "source": "0",
            "target": "-" + str(teacherId),
            "visited": "共" + str(weight),
            "core": True,
            "lineStyle": {
                "normal": {
                    # TODO 根据拜访次数设定连线宽度
                    "width": 10
                }
            }
        })

    return back


if __name__ == '__main__':
    # scholar_info(73927)
    print(get_relations("北京大学", "化学生物学与生物技术学院", ""))
    # new_schedule()
    # index()
    # edit_schedule()
    # set_whether_completed(100006,1,1)
    get_institution("清华大学")
    # pass
