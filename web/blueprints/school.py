import json
from flask import Blueprint, render_template,request
from flask_login import login_required

import web.service.school as school_service


school_bp = Blueprint('school', __name__)


@school_bp.route('/<school>')
@login_required
def index(school):
    """
    显示该学校的所有学院和相关的信息 树图
    :param school:
    :return:
    """
    school_info = school_service.get_school_info(school)
    school_intro = school+"拥有"+str(school_info['institutions'])+"个学院，"
    if school_info["dfc_num"] != 0:
        school_intro = school_intro + str(school_info['dfc_num'])+"个一流学科，"
    if school_info["nkd_num"] != 0:
        school_intro = school_intro + str(school_info['nkd_num'])+"个重点学科，"
    if school_info["skl_num"] != 0:
        school_intro = school_intro + str(school_info['skl_num'])+"个国家重点实验室，"
    if school_info["academician_num"] != 0:
        school_intro = school_intro + str(school_info['academician_num'])+"名院士，"
    if school_info["outstanding_num"] != 0:
        school_intro = school_intro + str(school_info['outstanding_num'])+"名杰出青年，"
    if school_info["cjsp_num"] != 0:
        school_intro = school_intro + str(school_info['cjsp_num'])+"名长江学者。"

    return render_template('school/index.html', school=school, school_intro=school_intro)


@school_bp.route('/get_institution_info',methods=["GET"])
@login_required
def get_institution_info():
    """
    获取重点学院和非重点学院
    :return:
    """
    school = request.args.get("school")
    data = school_service.get_institution_info(school)
    return json.dumps({"success":True,"data":data})


@school_bp.route('/<school>/<institution>')
@login_required
def institution(school, institution):
    """
    显示某一学校的学院的相关信息 主要是院系中的团队 关系图
    :param school:
    :param institution:
    :return:
    """
    return render_template('school/institution.html', school=school, institution=institution)


@school_bp.route('/<school>/<institution>/<int:team_index>')
@login_required
def show_team(school, institution, team_index):
    """
    显示某一个团队的相关信息 关系图
    :param school: 学校名
    :param institution: 学院名
    :param team_index: 团队的索引
    :return:
    """
    graph_data = school_service.get_team(school, institution, team_index)
    core_node = graph_data['core_node']
    return render_template('school/team.html', school=school, institution=institution,
                           graph_data=json.dumps(graph_data), core_node=core_node)
