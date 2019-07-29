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

        # 荣誉头衔排序，按时间，倒叙
        if 'honor_title' in basic_info and len(basic_info['honor_title']) > 0:
            basic_info['honor_title'].sort(key=lambda k: (k.get('year', 0)), reverse=True)

        # 获取基金集合
        if 'funds_id' in basic_info and len(basic_info["funds_id"]) > 0:
            basic_info["funds"] = getFundsInfo(mongo, basic_info["funds_id"])

        # 获取专利集合
        if 'patent_id' in basic_info and len(basic_info["patent_id"]) > 0:
            basic_info["patents"] = getPatentInfo(mongo, basic_info["patent_id"])

        # 获取论文数据集合
        if 'paper_id' in basic_info and len(basic_info["paper_id"]) > 0:
            basic_info["papers"] = getPatentInfo(mongo, basic_info["paper_id"])

        # 获取获奖情况
        if 'award_id' in basic_info and len(basic_info["award_id"]) > 0:
            basic_info["awards"] = getAwardInfo(mongo, basic_info["award_id"])

        # 计算教师年龄
        birth_year = basic_info["birth_year"]
        # 如果存在birth_year字段且为空，则不计算age
        if birth_year:
            basic_info['age'] = datetime.datetime.now().year - int(birth_year)

        """
        重点研发计划的部分未显示
        """

        return basic_info

    except Exception as e:
        print("------exception------  ", e)

    return basic_info


def getPatentInfo(mongo_link, objectId_list):
    """
    利用专利 objectId list获取 专利数据
    :param mongo_link: mongoDB 的连接
    :param objectId_list: list, not null
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
    :param objectId_list: list, not null
    :return: list
    """
    collection = mongo_link.get_collection("paper")
    info_list = collection.find({"_id": {"$in": list(objectId_list)}}, {"_id": 0}). \
        sort([("cited_num", -1), ("year", -1)]).limit(25)
    return list(info_list)


def getAwardInfo(mongo_link, objectId_list):
    """
    利用专利 objectId list获取 获奖数据
    :param mongo_link: mongoDB 的连接
    :param objectId_list: list, not null
    :return: list
    """
    collection = mongo_link.get_collection("awards")
    info_list = collection.find({"_id": {"$in": list(objectId_list)}}, {"_id": 0, "id": 0}).sort("year", -1).limit(25)
    return list(info_list)


def getFundsInfo(mongo_link, objectId_list):
    """
    """
    collection = mongo_link.get_collection("funds")
    info_list = collection.find({"_id": {"$in": list(objectId_list)}}, {"_id": 0}).\
        sort([("money", -1), ("year", -1)]).limit(25)

    return list(info_list)


if __name__ == '__main__':
    id_list = [73927,73928,73929,73930,73931,73932,73933,73934,73935,73936,73937,73938,73939,73940,73941,73942,73943,73944,73945,73946,73947,73948,73949,73950,73951,73952,73953,73954,73955,73956,73957,73958,73959,73960,73961,73962,73963,73964,73965,73966,73967,73968,73969,73970,73971,73972,73973,73974,73975,73976,73977,73978,73979,73980,73981,73982,73983,73984,73985,73986,73987,73988,73989,73990,73991,73992,73993,73994,73995,73996,73997,73998,73999,74000,74001,74002,74003,74004,74005,74006,74007,74008,74009,74010,74011,74012,74013,74014,74015,74016,74017,74018,74019,74020,74021,74022,74023,74024,74025,74026,74027,74028,74029,74030,74031,74032,74033,74034,74035,74036,74037,74038,74039,74040,74041,74042,74043,74044,74045,74046,74047,74048,74049,74050,74051,74052,74053,74054,74055,74056,74057,74058,74059,74060,74061,74062,74063,74064,74065,74066,74067,74068,74069,74070,74071,74072,74073,74074,74075,74076,74077,74078,74079,74080,74081,74082,74083,74084,74085,74086,74087,74088,74089,74090,74091,74092,74093,74094,74095,74096,74097,74098,74099,74100,74101,74102,74103,74104,74105,74106,74107,74108,74109,74110,74111,74112,74113,74114,74115,74116,74117,74118,74119,74120,74121,74122,74123,74124,74125,74126,74127,74128,74129,74130,74131,74132,74133,74134,74135,74136,74137,74138,74139,74140,74141,74142,74143,74144,74145,74146,74147,74148,74149,74150,74151,74152,74153,74154,74155,74156,74157,74158,74159,74160,74161,74162,74163,74164,74165,74166,74167,74168,74169,74170,74171,74172,74173,74174,74175,74176,74177,74178,74179,74180,74181,74182,74183,74184,74185,74186,74187,74188,74189,74190,74191,74192,74193,74194,74195,74196,74197,74198,74199,74200,74201,74202,74203,74204,74205,74206,74207,74208,74209,74210,74211,74212,74213,74214,74215,74216,74217,74218,74219,74220,74221,74222,74223,74224,74225,74226,74227,74228,74229,74230,74231,74232,74233,74234,74235,74236,74237,74238,74239,74240,74241,74242,74243,74244,74245,74246,74247,74248,74249,74250,74251,74252,74253,74254,74255,74256,74257,74258,74259,74260,74261,74262,74263,74264,74265,74266,74267,74268,74269,74270,74271,74272,74273,74274,74275,74276,74277,74278,74279,74280,74281,74282,74283,74284,74285,74286,74287,74288,74289,74290,74291,74292,74293,74294,74295,74296,74297,74298,74299,74300,74301,74302,74303,74304,74305,74306,74307,74308,74309,74310,74311,74312,74313,74314,74315,74316,74317,74318,74319,74320,74321,74322,74323,74324,74325,74326,74327,74328,74329,74330,74331,74332,74333,74334,74335,74336,74337,74338,74339,74340,74341,74342,74343,74344,74345,74346,74347,74348,74349,74350,74351,74352,74353,74354,74355,74356,74357,74358,74359,74360,74361,74362,74363,74364,74365,74366,74367,74368,74369,74370,74371,74372,74373,74374,74375,74376,74377,74378,74379,74380,74381,74382,74383,74384,74385,74386,74387,74388,74389,74390,74391,74392,74393,74394,74395,74396,74397,74398,74399,74400,74401,74402,74403,74404,74405,74406,74407,74408,74409,74410,74411,74412,74413,74414,74415,74416,74417,74418,74419,74420,74421,74422,74423,74424,74425,74426,74427,74428,74429,74430,74431,74432,74433,74434,74435,74436,74437,74438,74439,74440,74441,74442,74443,74444,74445,74446,74447,74448,74449,74450,74451,74452,74453,74454,74455,74456,74457,74458,74459,74460,74461,74462,74463,74464,74465,74466,74467,74468,74469,74470,74471,74472,74473,74474,74475,74476,74477,74478,74479,74480,74482,74483,74485,74486,74488,74494,74495,74496,74497,74498,74499,74500,74501,74502,74503,74504,74507,74508,74509,74510,74511,74512,74513,74514,74515,74516,74517,74518,74519,74520,74521,74522,74523,74524,74525,74526,74527,74528,74529,74530,74531,74532,74533,74534,74535,74536,74537,74538,74539,74540,74541,74542,74543,74544,74545,74546,74547,74548,74549,74550,74551,74552,74553,74554,74555,74556,74557,74558,74559,74560,74561,74562,74563,74564,74565,74566,74567,74568,74569,74570,74571,74572,74573,74574,74575,74576,74577,74578,74579,74580,74581,74582,74583,74584,74585,74586,74587,74588,74589,74590,74591,74592,74593,74594,74595,74596,74597,74598,74599,74600,74601,74602,74603,74604,74605,74606,74607,74608,74609,74610,74611,74612,74613,74614,74615,74616,74617,74618,74619,74620,74621,74622,74623,74624,74625,74626,74627,74628,74629,74630,74631,74632,74633,74634,74635,74636,74637,74638,74639,74640,74641,74642,74643,74644,74645,74646,74647,74648,74649,74650,74651,74652,74653,74654,74655,74656,74657,74658,74659,74660,74661,74662,74663,74664,74665,74666,74667,74668,74669,74670,74671,74672,74673,74674,74675,74676,74677,74678,74679,74680,74681,74682,74683,74684,74685,74686,74687,74688,74689,74690,74691,74692,74693,74694,74695,74696,74697,74698,74699,74700,74701,74702,74703,74704,74705,74706,74707,74708,74709,74710,74711,74712,74713,74714,74715,74716,74717,74718,74719,74720,74721,74722,74723,74724,74725,74726,74727,74728,74729,74730,74731,74732,74733,74734,74735,74736,74737,74738,74739,74740,74741,74742,74743,74744,74745,74746,74747,74748,74749,74750,74751,74752,74753,74754,74755,74756,74757,74758,74759,74760,74761,74762,74763,74764,74765,74766,74767,74768,74769,74770,74771,74772,74773,74774,74775,74776,74777,74778,74779,74780,74781,74782,74783,74784,74785,74786,74787,74788,74789,74790,74791,74792,74793,74794,74795,74796,74797,74798,74799,74800,74801,74802,74803,74804,74805,74806,74807,74808,74809,74810,74811,74812,74813,74814,74815,74816,74817,74818,74819,74820,74821,74822,74823,74824,74825,74826,74827,74828,74829,74830,74831,74832,74833,74834,74835,74836,74837,74838,74839,74840,74841,74842,74843,74844,74845,74846,74847,74848,74849,74850,74851,74852,74853,74854,74855,74856,74857,74858,74859,74860,74861,74862,74863,74864,74865,74866,74867,74868,74869,74870,74871,74872,74873,74874,74875,74876,74877,74878,74879,74880,74881,74882,74883,74884,74885,74886,74887,74888,74889,74890,74891,74892,74893,74894,74895,74896,74897,74898,74899,74900,74901,74902,74903,74904,74905,74906,74907,74908,74909,74910,74911,74912,74913,74914,74915,74916,74917,74918,74919,74920,74921,74922,74923,74924,74925,74926,74927,74928,74929,74930,74931,74932,74933,74934,74935,74936]
    count = len(id_list)
    avg = 0
    for i in range(count):
        avg += get_info(id_list[i])
    # print(back)
    print(avg / count)