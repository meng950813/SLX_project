import os
import json

from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator
from web.settings import basedir


def get_schools_institutions(cur_school=None, mongo=None):
    """
    获取目前的所有的学校和cur_school对应的所有学院
    :param cur_school: 当前选中的学校，如为None则默认获取第一个
    :param mongo: 为空则自己创建一个mongo
    :return: (学校数组,学院列表)
    """
    pass
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    # 获取学校
    collection = mongo.get_collection('school')
    generator = collection.find({}, {'_id': 0, 'name': 1})
    schools = [school['name'] for school in generator]
    # 确定当前选择的学校
    cur_school = schools[0] if cur_school is None else cur_school
    # 获取当前学校的所有院系
    school = collection.find_one({'name': cur_school}, {'_id': 0, 'institutions': 1})
    institutions = [result['name'] for result in school['institutions']]
    return cur_school, schools, institutions


def get_team(school, institution, team_index):
    """
    获取院系的某一个团队
    :param school: 学校的名称
    :param institution: 学院名
    :param team_index: 团队id
    :return:False 或者dict
    """
    file_path = os.path.join(basedir, 'web', 'static', 'relation_data', '%s%s.txt' % (school, institution))
    # 判断该学院社区网络文件是否存在
    if not os.path.exists(file_path):
        print("%s %s 的社交网络尚未生成！" % (school, institution))
        return False

    with open(file_path, "r") as f:
        # 获取所有的相关节点
        data = json.loads(f.read())
        relation_data = filter_data(data, team_index)
        # 获取所有的老师id
        teacher_ids = relation_data['teacher_ids']
        teacher_map = get_details(teacher_ids)
        categories = []
        # 重新设置类别
        nodes = relation_data['nodes']
        for node in nodes:
            teacher_id = int(node['name'])
            detail = teacher_map.get(teacher_id, None)
            try:
                index = categories.index(detail['title'])
            except (KeyError, ValueError):
                categories.append(detail['title'])
                index = len(categories) - 1
            node['category'] = index

        del relation_data['teacher_ids']
        relation_data['categories'] = [{'name': c} for c in categories]
        return relation_data


def filter_data(data, team_index):
    """
    根据team_index过滤出仅这个团队的成员节点和联系
    :param data: dict数据
    :param team_index: 团队索引
    :return: dict
    """
    nodes = []
    ids = []
    core_node = ""
    for node in data['nodes']:
        if node['class'] == team_index:
            nodes.append(node)
            ids.append(node['teacherId'])

            node['label'], node['name'] = node['name'], str(node['teacherId'])
            node['category'], node["draggable"] = 1, True
            node['symbolSize'] = int(node['centrality'] * 30 + 5)
            # 核心节点
            if node['teacherId'] in data["core_node"]:
                node["itemStyle"] = {
                    "normal": {"borderColor": 'yellow', "borderWidth": 2, "shadowBlur": 10,
                               "shadowColor": 'rgba(0, 0, 0, 0.3)'}}
                core_node = node['label']

            del node["teacherId"], node["class"], node["centrality"], node["code"], node["school"], node["insititution"]
    # 链接
    links = []
    for link in data["edges"]:
        if "source" not in link or "target" not in link:
            print("缺少 起点 / 终点：", link)
        elif link['source'] in ids and link['target'] in ids:
            link["source"], link["target"] = str(link["source"]), str(link["target"])
            link["value"] = link["weight"]
            if "weight" in link:
                del link['weight']
            links.append(link)
    # 覆盖
    relation_data = {
        "nodes": nodes,
        "links": links,
        "core_node": core_node,
        'teacher_ids': ids,
    }
    return relation_data


def get_details(teacher_ids):
    """
    根据老师的id数组获取老师的相关信息
    :param teacher_ids:
    :return:
    """
    mongo = MongoOperator(**MongoDB_CONFIG)
    # 获取学校
    collection = mongo.get_collection('basic_info')
    condition = {'id': {'$in': teacher_ids}}
    teachers = collection.find(condition, {'_id': 0, 'id': 1, 'title': 1, 'honor_title': 1})
    teacher_map = {}
    for teacher in teachers:
        if len(teacher['honor_title']) > 0:
            teacher['title'] = teacher['honor_title'][0]['type']
        elif len(teacher['title'].strip()) == 0:
            teacher['title'] = '未知'
        teacher_map[teacher['id']] = teacher

    return teacher_map
