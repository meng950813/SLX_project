import json
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

import web.service.school as school_service
from web.service.school_agent_service import agent_service
from web.utils import rich_abort

school_bp = Blueprint('school', __name__)


@school_bp.route('/<school>')
@login_required
def index(school):
    """
    显示该学校的所有学院和相关的信息 树图
    :param school:
    :return:
    """
    objects = school_service.get_school_info(school)
    if objects is None:
        rich_abort(404, '未找到该学校的信息，请确认学校名称后重试')
    subjects = []
    return render_template('school/index.html', school=school, objects=objects, subjects=subjects)


@school_bp.route('/get_institution_info', methods=["GET"])
@login_required
def get_institution_info():
    """
    获取重点学院和非重点学院
    :return:
    """
    school = request.args.get("school")
    data = school_service.get_total_institutions(school)
    return json.dumps({"success": True, "data": data})


@school_bp.route('/<school>/<institution>')
@login_required
def show_institution(school, institution):
    """
    显示某一学校的学院的相关信息 主要是院系中的团队 关系图
    :param school:
    :param institution:
    :return:
    """
    # 获取院系的关系网络
    graph_json = agent_service.get_relations(school, institution)
    if graph_json is False:
        rich_abort(404, '暂时没有该学院的社交网络，请确认名称或联系管理员')
    # 获取拜访次数
    subjects = school_service.get_related_teachers(current_user.related_teacher, json.loads(graph_json))
    # 获取客观信息
    objects = school_service.get_institution_info(school, institution)
    if objects is None:
        rich_abort(404, '未找到关于该学校和学院的相关信息，请确认后重试')

    return render_template('school/institution.html', school=school, institution=institution,
                           objects=objects, subjects=subjects, graph_json=graph_json)


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
    graph_data, objects = school_service.get_team(school, institution, team_index)
    # 学校或者是学院不存在
    if graph_data is False:
        rich_abort(404, '暂时没有该学院的社交网络，请确认名称或联系管理员')
    # 团队不存在
    core_node = graph_data['core_node']
    if len(core_node) == 0:
        rich_abort(404, '未找到该团队')
    # 获取当前用户的有联系的老师
    subjects = school_service.get_related_teachers(current_user.related_teacher, graph_data)

    return render_template('school/team.html', school=school, institution=institution,
                           graph_data=json.dumps(graph_data), core_node=core_node,
                           objects=objects, subjects=subjects)
