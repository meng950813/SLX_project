"""
2019.7.3
by zhang
"""

import pymongo
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


def search_teacher_basic_info(teacher_id):
    """
    根据教师的id从MongoDB中获取教师的基本信息
    :param teacher_id:
    :return:
    """

    mongo_operator = MongoOperator(**MongoDB_CONFIG)
    # 指定集合
    basic_info_dict = mongo_operator.find_one({"id": teacher_id}, "basic_info")

    # 利用基本信息表中的patent索引_id 搜索patent集合中对应的数据
    # 并将其加入到basic_info_dict中
    if "patent_id" in basic_info_dict:
        patent_id_list = basic_info_dict["patent_id"]
        patent_info_list = []
        for patent_id in patent_id_list:
            patent_info = mongo_operator.find_one({"_id": patent_id}, "patent")
            # print(patent)
            del patent_info["_id"]
            patent_info_list.append(patent_info)

        basic_info_dict["patent"] = patent_info_list

        del basic_info_dict["patent_id"]

    # 利用基本信息表中的fund索引_id 搜索funds集合中对应的数据
    # 并将其加入到basic_info_dict中
    if "funds_id" in basic_info_dict:
        funds_id_list = basic_info_dict["funds_id"]
        funds_info_list = []

        for funds_id in funds_id_list:
            funds_info = mongo_operator.find_one({"_id": funds_id}, "funds")
            del funds_info["_id"]
            print(funds_info)

            funds_info_list.append(funds_info)
        basic_info_dict["funds"] = funds_info_list

        del basic_info_dict["funds_id"]

    # 由于MongoDB中的默认id是
    del basic_info_dict["_id"]
    """
    重点研发计划的部分未显示
    """
    return basic_info_dict


if __name__ == '__main__':
    # p = Project()
    search_teacher_basic_info(73932)
