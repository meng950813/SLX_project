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


def get_school_info(school_name, mongo=None):
    """
    根据学校名获取学校的简介信息
    :param school_name: 学校名
    :param mongo: MongoOperator对象
    :return: school_info: 学校名，学院数量，一流学科数量，重点学科数量，国家重点实验室数量，院士数量，长江学者数量，杰出青年数量
    :return ((院士，2)...)
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("school")
    school_info = collection.find_one({"name": school_name}, {"_id": 0, "institutions": 1, "dfc_num": 1, "nkd_num": 1,
                                                              "skl_num": 1, "academician_num": 1, "outstanding_num": 1,
                                                              "cjsp_num": 1})

    keys = [('academician_num', '院士'), ('cjsp_num', '长江学者'), ('dfc_num', '一流学科'),
            ('nkd_num', '重点学科'), ('outstanding_num', '杰出青年'), ('skl_num', '重点实验室')]
    objects = []
    for key, value in keys:
        objects.append((value, school_info[key]))
    return objects


def get_institution_info(school_name, mongo=None):
    """
    根据学校名获取学校中的重点学院和非重点学院，将有一流学科、重点学科和国家重点实验室
    :param school_name:学校名
    :param mongo:为空则自己创建一个mongo
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    institution = collection.find({"school": school_name}, {"_id": 0, "institution": 1, "dfc_num": 1, "nkd_num": 1,
                                                            "skl_num": 1})
    # 重点学院
    main_institution = []
    # 非重点学院
    dis_main_institution = []
    for i in institution:
        # 筛选同时拥有一流学科和重点学科的学院或者拥有国家重点实验室的学院为重点学院
        if (i['dfc_num'] > 0 and i['nkd_num'] > 0) or i['skl_num'] > 0:
            main_institution.append(i['institution'])
        else:
            dis_main_institution.append(i['institution'])
    data = {}
    data['name'] = school_name
    data['children'] = []

    main_institution_dict = {}
    main_institution_dict['name'] = "重点学院"
    main_institution_children = []
    for i in main_institution:
        main_institution_children.append({"name": i})
    main_institution_dict['children'] = main_institution_children

    dis_main_institution_dict = {}
    dis_main_institution_dict['name'] = "非重点学院"
    dis_main_institution_children = []
    for i in dis_main_institution:
        dis_main_institution_children.append({"name": i})
    dis_main_institution_dict['children'] = dis_main_institution_children

    data['children'].append(main_institution_dict)
    data['children'].append(dis_main_institution_dict)

    return data


def get_team(school, institution, team_index):
    """
    获取院系的某一个团队 category为头衔或者荣誉
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
        relation_data = _filter_teachers(data, team_index)
        # 获取所有的老师id
        teacher_ids = relation_data['teacher_ids']
        teacher_map = get_details(teacher_ids)
        categories = []
        # 保留客观数据 各种头衔及其人数
        subjects = {}
        for _, teacher in teacher_map.items():
            titles = [title['type'] for title in teacher['honor_title']]
            titles.append(teacher['title'])
            for title in titles:
                if len(title.strip()) == 0:
                    continue
                if title in subjects:
                    subjects[title] += 1
                else:
                    subjects[title] = 1
        # 重新设置类别
        nodes = relation_data['nodes']
        for node in nodes:
            teacher_id = int(node['name'])
            detail = teacher_map.get(teacher_id, None)
            try:
                index = categories.index(detail['category'])
            except (KeyError, ValueError):
                categories.append(detail['category'])
                index = len(categories) - 1
            node['category'] = index

        del relation_data['teacher_ids']
        relation_data['categories'] = [{'name': c} for c in categories]
        return relation_data, subjects


def _filter_teachers(data, team_index):
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
            teacher['category'] = teacher['honor_title'][0]['type']
        elif len(teacher['title'].strip()) == 0:
            teacher['category'] = '未知'
        else:
            teacher['category'] = teacher['title']
        teacher_map[teacher['id']] = teacher

    return teacher_map


def get_related_teachers(related_teachers, graph_data):
    """
    根据图数据，获取与当前用户建立联系的(老师名，次数)数组
    :param related_teachers: 有联系的老师数组
    :param graph_data: 图数据
    :return: (老师名，拜访次数) 数组
    """
    # 获取当前用户的有联系的老师
    related_teacher_ids = []
    related_teacher_cnts = []

    for teacher in related_teachers:
        related_teacher_ids.append(str(teacher['id']))
        related_teacher_cnts.append(teacher['visited_count'])
    subjects = []
    # 获取这个院系的节点信息
    for node in graph_data['nodes']:
        try:
            i = related_teacher_ids.index(node['name'])
            subjects.append((node['label'], related_teacher_cnts[i]))
        except ValueError:
            pass
    return subjects


if __name__ == "__main__":
    ins = get_institution_info("清华大学")
    print(ins)
    pass
