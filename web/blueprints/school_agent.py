from flask import Blueprint, render_template, request
import json
import os
import threading
from flask_login import current_user

from web.blueprints.auth import login_required
from web.utils.mongo_operator import MongoOperator
from web.config import MongoDB_CONFIG
from web.settings import basedir
from web.service.user_service import check_user
from web.utils.encrypt import encryption

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
    uid = current_user.id

    if "charge_school" in current_user:
        user_info = {
            'charge_school': current_user['charge_school'],
            "related_teacher": current_user['related_teacher']
        }
    else:
        # 获取该商务的信息
        user_info = mongo_operator.get_collection("user").find_one({"id": uid})

        if not ("related_teacher" in user_info):
            user_info["related_teacher"] = None

        if not ("charge_school" in user_info):
            user_info["charge_school"] = None

        current_user["charge_school"] = user_info['charge_school']
        current_user["related_teacher"] = user_info["related_teacher"]

    schools = user_info['charge_school']

    if schools:
        # 仅仅获取第一个学校的学院数组
        institutions = get_institutions_list(schools[0])

        return render_template('personal.html', schools=schools, institutions=institutions)
    else:
        return render_template('personal.html', schools=[], institutions=[])


@school_agent_bp.route('/change_school', methods=["GET"])
@login_required
def change_school():
    school = request.args.get("school")
    institutions = get_institutions_list(school)
    if institutions:
        return json.dumps(institutions)
    return json.dumps({"success": False, "message": "学校名有误"})


@school_agent_bp.route('/get_schools', methods=['GET'])
@login_required
def get_schools():
    """
    by zhang
    获取所有学校的名称组成的列表
    :return:
    """
    mongo = MongoOperator(**MongoDB_CONFIG)
    try:
        school_col = mongo.get_collection("school")
        schools = list(school_col.find({}, {"_id": 0, "name": 1}))

        # 转成学校列表
        school_list = [d["name"] for d in schools]
        return json.dumps({"success": True, "school_list": school_list})

    except:
        return json.dumps({"success": True, "school_list": []})


@school_agent_bp.route('/change_institution', methods=["GET", "PUT"])
@login_required
def change_institution():
    school = request.args.get("school")
    institution = request.args.get("institution")
    get_relation = request.args.get("relation")
    
    # 个人中心需要获取关系数据
    if get_relation:
        json_data = get_relations(school, institution, current_user.get("related_teacher"))

        if json_data:
            # 放在此处执行 + 1 操作是为了让无关系文件的学院靠后
            # 多线程执行访问数 +1
            add_thead = threading.Thread(target=add_institution_click_time, args=(school, institution))
            add_thead.start()
            
            return json_data
        else:
            return json.dumps({"success": False, "message": "暂无当前学院的社交网络数据"})

    # 多线程执行访问数 +1
    add_thead = threading.Thread(target=add_institution_click_time, args=(school, institution))
    add_thead.start()
    
    return json.dumps({"success": True})


def get_institutions_dict(school):
    """
    获取学校所有的学院信息，按 visited 排序
    :param school: str 学校名
    :return: [{"name":xxx, "visited": 132},...] or False
    """
    back = MongoOperator(**MongoDB_CONFIG).get_collection("school").find_one({"name": school}, {"institutions": 1})
    if not back or not ("institutions" in back):
        return False
    
    institutions = back['institutions']
    # 按照学院被点击次数排序 ==> [{"visited":xx, "name":xx}, ...]
    institutions.sort(key=lambda k: k.get("visited"), reverse=True)
    # 取出学院名，转为dict
    return institutions


def get_institutions_list(school):
    """
    获取学校所有的学院信息，按 visited 排序
    :param school: str 学校名
    :return: [xxx,xxx,xxx...] or False
    """
    institutions = get_institutions_dict(school)
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
    file_path = os.path.join(basedir, 'web', 'static', 'relation_data', '%s%s.txt' % (school, institution))

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


def add_institution_click_time(school, institution):
    """
    更新指定学院的点击次数 +1
    :param school: 学校名
    :param institution: 学院名
    :return:
    """
    try:
        school_collection = MongoOperator(**MongoDB_CONFIG).get_collection("school")

        # {'_id': ObjectId('xxx'), 'institutions': [{'visited': 2, 'name': '公共卫生学院'}]}
        back = school_collection.find_one({"name": school, "institutions.name": institution}, {"institutions.$.visited":1})
        visited = int(back['institutions'][0]["visited"]) + 1
        # 该学院增加一次点击
        school_collection.update_one(
            {"name": school, "institutions.name": institution}, {"$set": {"institutions.$.visited": visited }})
    except Exception as e:
        print("点击次数加一失败， visited=%s")
        print(e)


@school_agent_bp.route('/setting')
@login_required
def setting():
    """
    by zhang
    商务修改个人信息
    :return:修改基本信息的页面
    """

    return render_template('change_basic_info.html')


@school_agent_bp.route('/get_user_info')
@login_required
def get_user_info():
    """
    获取具体的个人信息
    :return:json格式的用户字典
    """

    type = current_user.type
    user_type = ""
    if type == "0":
        user_type = "学校商务"
    elif type == "1":
        user_type = "企业商务"
    else:
        user_type = "其他用户"

    user_dict = {
        "user_id": current_user.id,
        "user_name": current_user.name,
        "user_tel": current_user.tel_number,
        "user_email": current_user.email,
        "user_pwd": current_user.password,
        "user_type": user_type,
        "charge_school": current_user.charge_school,
        "related_teacher": current_user.related_teacher
    }

    return json.dumps(user_dict)


@school_agent_bp.route('/save_basic_info', methods=["POST"])
@login_required
def save_basic_info():
    """
    保存用户修改的基本信息
    :return:修改成功： {"success": True}， 修改失败： {"success": False}
    """

    user_id = request.form.get("user_id")
    user_id = int(user_id)

    user_name = request.form.get("user_name")
    user_email = request.form.get("user_email")
    user_tel = request.form.get("user_tel")

    mongo = MongoOperator(**MongoDB_CONFIG)

    user_col = mongo.get_collection("user")

    try:
        update_res = user_col.update({'id': user_id}, {"$set": {
            "name": user_name,
            "email": user_email,
            "tel_number": user_tel,
        }})

        if update_res['nModified'] != 0:
            current_user.name = user_name
            current_user.email = user_email
            current_user.tel_number = user_tel

        return json.dumps({"success": True})
    except:
        return json.dumps({"success": False})


@school_agent_bp.route('/school_agent/basic_info')
@login_required
def basic_info():
    """

    :return:
    """
    return render_template('change_basic_info.html')


@school_agent_bp.route('/school_agent/change_pwd')
@login_required
def change_pwd():
    """
    点击修改密码按钮时跳转页面
    :return:修改密码的页面
    """
    return render_template('change_pwd.html')


@school_agent_bp.route('/vertify_pwd/<old_pwd>')
@login_required
def vertify_pwd(old_pwd):
    """
    修改密码时验证 输入的原密码
    :param old_pwd:输入的原密码
    :return:原密码验证失败： {"success": False}， 验证成功： {"success": True}
    """
    user_name = current_user.name

    res = encryption(old_pwd)

    if res != current_user.password:
        return json.dumps({"success": False})
    else:
        return json.dumps({"success": True})


@school_agent_bp.route('/change_pwd_in_db/<new_pwd>')
@login_required
def change_pwd_in_db(new_pwd):
    """
    根据输入的新密码对用户数据库中的密码进行修改
    :param new_pwd:新密码
    :return:密码修改失败： {"success": False}， 修改成功： {"success": True}
    """

    user_id = current_user.id
    pwd_md5 = encryption(new_pwd)
    try:
        mongo = MongoOperator(**MongoDB_CONFIG)
        user_col = mongo.get_collection("user")
        user_col.update({"id": user_id}, {"$set": {"password": pwd_md5}})
        return json.dumps({"success": True})
    except:
        return json.dumps({"success": False})


# if __name__ == '__main__':
#     # scholar_info(73927)
#     print(get_relations("北京大学", "化学生物学与生物技术学院", ""))
#     # new_schedule()
#     # index()
#     # edit_schedule()
#     # set_whether_completed(100006,1,1)
#     get_institutions_list("清华大学")
#     # pass
