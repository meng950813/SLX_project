# -*- coding:utf-8 -*-
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
    :return ((院士，数目)...)
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("school")
    school_info = collection.find_one({"name": school_name}, {"_id": 0, "institutions": 1, "dfc_num": 1, "nkd_num": 1,
                                                              "skl_num": 1, "academician_num": 1, "outstanding_num": 1,
                                                              "cjsp_num": 1})
    if school_info is None:
        return None

    keys = [('academician_num', '院士'), ('cjsp_num', '长江学者'), ('dfc_num', '一流学科'),
            ('nkd_num', '重点学科'), ('outstanding_num', '杰出青年'), ('skl_num', '重点实验室')]
    objects = []
    for key, value in keys:
        objects.append((value, school_info[key]))
    return objects


def get_institution_info(school, institution):
    """
    获取学校中该学院的相关信息
    :param school: 学校名称
    :param institution: 学院名称
    :return: 学科、荣誉头衔和个数tuple数组，如果不存在学校.学院则返回None
    """
    mongo = MongoOperator(**MongoDB_CONFIG)
    # 获取学校
    collection = mongo.get_collection('institution')
    result = collection.find_one({'school': school, 'institution': institution},
                                 {'_id': 0, 'school': 0, 'institution': 0})
    # 学校或院系不存在
    if result is None:
        return None
    keys = [('academician_num', '院士'), ('cjsp_num', '长江学者'), ('dfc_num', '一流学科'),
            ('nkd_num', '重点学科'), ('outstanding_num', '杰出青年'), ('skl_num', '重点实验室')]
    objects = []
    for key, value in keys:
        objects.append((value, result[key]))
    return objects


def get_total_institutions(school_name, mongo=None):
    """
    根据学校名获取学校中的重点学院和非重点学院，将有一流学科并且有重点学科或者拥有国家重点实验室的学院定位重点学院
    :param school_name:学校名
    :param mongo:为空则自己创建一个mongo
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    institution = collection.find({"school": school_name,"relation_data":1,"select":1}, {"_id": 0, "institution": 1, "dfc_num": 1, "nkd_num": 1,
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


def is_exist_data(school,institution):
    """
    判断学院文件是否存在
    :return:有则返回1，无则返回0
    """
    file_path = os.path.join(basedir, 'web', 'static', 'relation_data', '%s%s.txt' % (school, institution))
    if os.path.exists(file_path):
        return True
    else:
        return False

def get_institution(school,mongo=None):
    """
    获取mongo数据库中没有关系网络的学校学院
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    institution = collection.find({"school":school,"relation_data":0},{"_id": 0,"school":1,"institution":1})
    return institution


def get_all_institution(school,mongo=None):
    """
    获取mongo数据库中此学校的所有学院
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    institution_list = collection.find({"school":school},{"_id": 0,"institution":1})
    institution = []
    for i in institution_list:
        institution.append(i['institution'])
    return institution

def update_institution_relation_data(school,institution, mongo=None):
    """
    有此学校学院的关系数据网络则在此学院的字段添加字段relation_data为1，否则为0
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    if(is_exist_data(school,institution)):
        collection.update_one({"school":school,"institution":institution},{"$set":{"relation_data":1}})
    else:
        collection.update_one({"school":school,"institution":institution},{"$set":{"relation_data":0}})


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
        teacher_map = _get_details(teacher_ids)
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


def _get_details(teacher_ids):
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


def get_edit_institution(school,mongo=None):
    """
    获取mongo数据库中所有的学校学院
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    institution_list = collection.find({"school":school,"relation_data":1},{"_id": 0,"select":1,"institution":1,"dfc_num": 1, "nkd_num": 1,
                                                            "skl_num": 1})
    institution = {}
    institution['main_institution'] = []
    institution['dis_main_institution'] = []
    institution['no_relation_data'] = []
    for i in institution_list:
        if (i['dfc_num'] > 0 and i['nkd_num'] > 0) or i['skl_num'] > 0:
            institution['main_institution'].append([i['institution'],i['select']])
        else:
            institution['dis_main_institution'].append([i['institution'],i['select']])
    return institution

def update_institution_select(school,institution_select,mongo=None):
    """
    更新institution中select字段
    :param school: 学校名
    :param institution_select: 选择的学院信息
    :param mongo: 数据库
    :return:
    """
    if mongo is None:
        mongo = MongoOperator(**MongoDB_CONFIG)
    collection = mongo.get_collection("institution")
    for i in institution_select:
        collection.update_one({"school":school,"institution":i[0]},{"$set":{"select":i[1]}})

if __name__ == "__main__":
    # ins = get_all_institution("清华大学")
    # print(ins)
    # ins  = [['信息科学技术学院', 1], ['机械工程学院', 1], ['五道口金融学院', 0], ['交叉信息研究院', 0], ['人文学院', 0], ['体育部', 0], ['公共管理学院', 0], ['化学工程系', 0], ['医学院', 0], ['周培源应用数学研究中心', 0], ['土木水利学院', 0], ['工程物理系', 0], ['建筑学院', 0], ['教育研究院', 0], ['数学科学中心', 0], ['新闻与传播学院', 0], ['材料学院', 0], ['核能与新能源技术研究院', 0], ['法学院', 0], ['深圳研究院（信息与技术学部）', 0], ['深圳研究院（先进制造学部）', 0], ['深圳研究院（海洋科学与技术学部）', 0], ['深圳研究院（物流与交通学部）', 0], ['深圳研究院（生命与健康学部）', 0], ['深圳研究院（社会科学与管理学部）', 0], ['深圳研究院（能源与环境学部）', 0], ['燃烧能源中心', 0], ['环境学院', 0], ['理学院', 0], ['生命科学学院', 0], ['电机工程与应用电子技术系', 0], ['社会科学学院', 0], ['经济管理学院', 0], ['美术学院', 0], ['航天航空学院', 0], ['艺术教育中心', 0], ['药学院', 0], ['马克思主义学院', 0], ['高等研究院', 0]]

    # update_institution_select("清华大学",ins)
    ins = get_edit_institution("清华大学")
    print(ins)
    pass