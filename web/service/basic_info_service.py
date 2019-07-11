"""
2019.7.3
by zhang
"""

from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator


def search_teacher_basic_info(teacher_id):
    """
    根据教师的id从MongoDB中获取教师的基本信息
    :param teacher_id:
    :return:
    """
    print("-------------------------开始搜索学者基本信息---------------------------------------")
    try:
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        # 指定集合
        basic_info_dict = mongo_operator.find_one({"id": teacher_id}, "basic_info")
        # 获取基本信息集合中的教师专利的引用列表
        patent_id_list = basic_info_dict["patent_id"]
        # 将其装换为python的列表
        patent_id_list = list(patent_id_list)
        # print(patent_id_list)

        # 获取专利集合
        patent_col = mongo_operator.get_collection("patent")
        # 获取有用的信息 删除其中的ObjectId对象
        patent_list = patent_col.find({"_id": {"$in": patent_id_list}}, {
            "_id": 0,
            "author_list": 1,
            "date": 1,
            "title": 1,
            "id": 1,
            "proposer": 1
        })
        patent_list = list(patent_list)

        # 获取基本信息集合中的教师基金的引用列表
        funds_id_list = basic_info_dict["funds_id"]
        # 获取基金集合
        funds_col = mongo_operator.get_collection("funds")
        # 删除其中的ObjectId对象
        funds_list = funds_col.find({"_id": {"$in": funds_id_list}}, {"_id": 0})
        funds_list = list(funds_list)

        # 添加入基本信息列表
        basic_info_dict["patent"] = patent_list
        basic_info_dict["funds"] = funds_list

        # 删除基本信息中的_id
        del basic_info_dict["_id"]
        
        """
        重点研发计划的部分未显示
        """
    except Exception as e:
        print("------exception------  ", e)

    return basic_info_dict


if __name__ == '__main__':
    # p = Project()
    search_teacher_basic_info(73964)
