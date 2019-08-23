"""
2019.7.3
by zhang
"""
import datetime
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator
from web.utils.neo4j_operator import NeoOperator
from web.config import NEO4J_CONFIG

def get_info(teacher_id):
    """
    根据教师的id从MongoDB中获取教师的基本信息
    :param teacher_id:
    :return:
    """
    basic_info = None

    try:
        mongo = MongoOperator(**MongoDB_CONFIG)
        # 是否存在该老师
        basic_info = mongo.get_collection('basic_info').find_one({'id': teacher_id}, {'_id': 0})
        if basic_info is None:
            return basic_info

        # 荣誉头衔排序，按时间，倒序
        if 'honor_title' in basic_info and len(basic_info['honor_title']) > 0:
            basic_info['honor_title'].sort(key=lambda k: (k.get('year', 0)), reverse=True)

        # 获取项目集合
        if 'project_id' in basic_info and len(basic_info["project_id"]) > 0:
            basic_info["projects"] = getProjectsInfo(mongo, basic_info["project_id"])

        # 获取专利集合
        if 'patent_id' in basic_info and len(basic_info["patent_id"]) > 0:
            basic_info["patents"] = getPatentInfo(mongo, basic_info["patent_id"])

        # 获取论文数据集合
        if 'paper_id' in basic_info and len(basic_info["paper_id"]) > 0:
            basic_info["papers"] = getPaperInfo(mongo, basic_info["paper_id"])

        # 获取获奖情况
        if 'award_id' in basic_info and len(basic_info["award_id"]) > 0:
            basic_info["awards"] = getAwardInfo(mongo, basic_info["award_id"])

        # 计算教师年龄
        birth_year = basic_info["birth_year"]
        # 如果存在birth_year字段且为空，则不计算age
        if birth_year:
            basic_info['age'] = datetime.datetime.now().year - int(birth_year)

        # print(basic_info)
        return basic_info

    except Exception as e:
        print("------exception------  ", e)

    return basic_info

def get_team_info(teacher_id_list):
    """
    根据教师团队的id收集
    :param teacher_id_list:教师团队中所有老师的ID
    :return:team_info:教师团队的项目、专利和论文数据
    """
    team_info = {}
    for i in teacher_id_list:
        try:
            mongo = MongoOperator(**MongoDB_CONFIG)
            # 是否存在该老师
            basic_info = mongo.get_collection('basic_info').find_one({'id': i}, {'_id': 0})
            print(basic_info)
            # 获取项目集合
            if 'funds_id' in basic_info and len(basic_info["project_id"]) > 0:
                team_info["funds"].append(getProjectsInfo(mongo, basic_info["project_id"]))

            # 获取专利集合
            if 'patent_id' in basic_info and len(basic_info["patent_id"]) > 0:
                team_info["patents"].append(getPatentInfo(mongo, basic_info["patent_id"]))

            # 获取论文数据集合
            if 'paper_id' in basic_info and len(basic_info["paper_id"]) > 0:
                team_info["papers"].append(getPaperInfo(mongo, basic_info["paper_id"]))
        except:
            pass
        return team_info

def getPatentInfo(mongo_link, objectId_list):
    """
    利用专利 objectId list获取 专利数据
    :param mongo_link: mongoDB 的连接
    :param objectId_list: 教师专利id列表
    :return: list
    """
    collection = mongo_link.get_collection("patent")
    patent_list = collection.find({"_id": {"$in": list(objectId_list)}}, {"_id": 0}). \
        sort("date", -1).limit(25)

    return list(patent_list)


def getPaperInfo(mongo_link, objectId_list):
    """
    利用专利 objectId list获取 论文数据
    :param mongo_link: mongoDB 的连接
    :param objectId_list: 教师论文id列表
    :return: list
    """
    collection = mongo_link.get_collection("paper")
    info_list = collection.find({"_id": {"$in": list(objectId_list)}},
                                {"_id": 0, "id": 0, "abstract": 0, "source": 0, "keyword": 0}).\
                                sort([("cited_num", -1), ("year", -1)]).limit(25)

    info_list = list(info_list)

    for item in info_list:
        if "author" in item:
            author = [i['name'] for i in item['author']]
            item["author"] = ",".join(author)

    return info_list


def getAwardInfo(mongo_link, objectId_list):
    """
    利用专利 objectId list获取 获奖数据
    :param mongo_link: mongoDB 的连接
    :param objectId_list: 教师获奖id列表
    :return: list
    """
    collection = mongo_link.get_collection("awards")
    info_list = collection.find({"_id": {"$in": list(objectId_list)}}, {"_id": 0, "id": 0}).sort("year", -1).limit(25)
    return list(info_list)


def getProjectsInfo(mongo_link, objectId_list):
    """
    """
    collection = mongo_link.get_collection("project_info")
    info_list = collection.find({"_id": {"$in": list(objectId_list)}}, {"_id": 0}).\
        sort([("money", -1), ("start_time", -1)]).limit(25)

    return list(info_list)


def get_teacher_central_network(teacher_id, school=None):
    """
    获取某一教师社交网络
    :param teacher_id: int
    :param school: 学校名，限定关系网的范围
    :return: [] or [
                {
                    "source": {id: teacher_id, name, shcool, institution, code},
                    "r" : {paper:xxx, patent:xxx, project:xxx}
                    "target":{id: xxx, name, school, institution, code}
                }, ...
            ]
    """

    try:
        if school:
            cql = "Match(source:Teacher{id:%d})-[r:学术合作]-(target:Teacher{school:%s}) " \
                  "return target.id as id" % (teacher_id, school)
        else:
            cql = "Match(source:Teacher{id:%d})-[r:学术合作]-(target:Teacher) " \
                  "return target.id as id, target.name as name" % teacher_id

        neo = NeoOperator(**NEO4J_CONFIG).get_connection()
        # dataType: [{"id":xxx, "name":xxx}, {...}, ...] or []
        result = neo.run(cql).data()
        return result
    except Exception as e:
        print(e)
        return []


if __name__ == '__main__':
    id_list = [73927, 73928, 73929, 73930, 73931, 73932, 73933]
