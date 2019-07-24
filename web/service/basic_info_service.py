"""
2019.7.3
by zhang
"""
import datetime
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


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

        # 获取专利集合
        if 'patent_id' in basic_info:
            collection = mongo.get_collection("patent")
            patent_list = collection.find({"_id": {"$in": list(basic_info['patent_id'])}}, {"_id": 0})
            basic_info["patent"] = list(patent_list)

        # 获取基金集合
        if 'funds_id' in basic_info:
            collection = mongo.get_collection("funds")
            funds_list = collection.find({"_id": {"$in": list(basic_info['funds_id'])}}, {"_id": 0})
            basic_info["funds"] = list(funds_list)
        # 计算教师年龄
        birth_year = basic_info["birth_year"]
        # 如果存在birth_year字段且为空，则不计算age
        if birth_year:
            basic_info['age'] = datetime.datetime.now().year - int(birth_year)
        """
        重点研发计划的部分未显示
        """
    except Exception as e:
        print("------exception------  ", e)

    return basic_info
