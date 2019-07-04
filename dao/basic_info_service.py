"""
2019.7.3
by zhang
"""

import pymongo
from nameko.rpc import rpc
import json

# from Nameko.config import DB_CONFIG

from config import MongoDB_CONFIG

class Project(object):
    name = "project"
    @rpc
    def search_teacher_basic_info(self, teacher_id):
        """
        根据教师的id从MongoDB中获取教师的基本信息
        :param teacher_id:
        :return:
        """

        # 连接服务器
        myclient = pymongo.MongoClient("mongodb://" + MongoDB_CONFIG["ip"] + ":" + MongoDB_CONFIG["port"])

        # 指定远程库
        mydb = myclient["new_db"]

        # 指定集合

        basic_col = mydb["basic_info"]

        basic_info_dict = basic_col.find_one({"id": teacher_id})


        # 利用基本信息表中的patent索引_id 搜索patent集合中对应的数据
        # 并将其加入到basic_info_dict中
        if "patent_id" in basic_info_dict:
            patent_col = mydb["patent"]
            patent_id_list = basic_info_dict["patent_id"]
            patent_info_list = []
            for patent_id in patent_id_list:
                patent_info = patent_col.find_one({"_id": patent_id})
                # print(patent)
                del patent_info["_id"]
                patent_info_list.append(patent_info)

            basic_info_dict["patent"] = patent_info_list

            del basic_info_dict["patent_id"]

        # 利用基本信息表中的fund索引_id 搜索funds集合中对应的数据
        # 并将其加入到basic_info_dict中
        if "funds_id" in basic_info_dict:
            funds_col = mydb["funds"]
            funds_id_list = basic_info_dict["funds_id"]
            funds_info_list = []

            for funds_id in funds_id_list:
                funds_info = funds_col.find_one({"_id": funds_id})
                del funds_info["_id"]
                print(funds_info)

                funds_info_list.append(funds_info)
            basic_info_dict["funds"] = funds_info_list

            del basic_info_dict["funds_id"]

        del basic_info_dict["_id"]


        """
        重点研发计划的部分未显示
        
        """


        print(basic_info_dict)


        return json.dumps(basic_info_dict, ensure_ascii=False)


if __name__ == '__main__':
    p = Project()
    p.search_teacher_basic_info(73932)
