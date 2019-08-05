import json
import os
import threading

from flask import Blueprint, render_template, request

from flask_login import current_user
from web.blueprints.auth import login_required
from web.config import MongoDB_CONFIG
from web.service.school_agent_service import agent_service
from web.utils.encrypt import encryption
from web.utils.mongo_operator import MongoOperator

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
    
    user_info = {}
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
        institutions = agent_service.get_institutions_list(schools[0])

        return render_template('personal.html', schools=schools, institutions=institutions)
    else:
        return render_template('personal.html', schools=[], institutions=[])


@school_agent_bp.route('/get_school_relation', methods=["GET"])
@login_required
def get_school_relation():
    school = request.args.get("school")
    # data ==> {nodes:[{},..], links:[{..},... , community:123]}
    data = agent_service.get_agent_relation_in_school(current_user.id, school)

    return json.dumps(data)


@school_agent_bp.route('/change_school', methods=["GET"])
@login_required
def change_school():
    school = request.args.get("school")
    institutions = agent_service.get_institutions_list(school)
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
        school_list = [school["name"] for school in schools]
        return json.dumps({"success": True, "school_list": school_list})
    except Exception as e:
        print(e)
        return json.dumps({"success": False, "school_list": []})


@school_agent_bp.route('/change_institution', methods=["GET", "PUT"])
@login_required
def change_institution():
    school = request.args.get("school")
    institution = request.args.get("institution")
    get_relation = request.args.get("relation")
    
    # 个人中心需要获取关系数据
    if get_relation:
        # json_data = agent_service.get_relations(school, institution, current_user.id)
        json_data = agent_service.get_relations(school, institution)

        if json_data:
            # 放在此处执行 + 1 操作是为了让无关系文件的学院靠后
            # 多线程执行访问数 +1
            add_thead = threading.Thread(target=agent_service.add_institution_click_time, args=(school, institution))
            add_thead.start()
            
            return json_data
        else:
            return json.dumps({"success": False, "message": "暂无当前学院的社交网络数据"})

    # 多线程执行访问数 +1
    add_thead = threading.Thread(target=agent_service.add_institution_click_time, args=(school, institution))
    add_thead.start()
    
    return json.dumps({"success": True})


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


if __name__ == '__main__':
    # scholar_info(73927)
    print(agent_service.get_relations("北京大学", "化学生物学与生物技术学院", ""))
    # new_schedule()
    # index()
    # edit_schedule()
    # set_whether_completed(100006,1,1)
    agent_service.get_institutions_list("清华大学")
    # pass