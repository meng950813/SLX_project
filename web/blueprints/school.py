from flask import Blueprint, render_template
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
        school_intro = school_intro + str(school_info['cjsp_num'])+"名长江学者，"

    return render_template('school/index.html', school=school, school_intro=school_intro)


@school_bp.route('/>school>/<institution>')
@login_required
def institution(school, institution):
    """
    显示某一学校的学院的相关信息 主要是院系中的团队 关系图
    :param school:
    :param institution:
    :return:
    """
    return render_template('school/base.html', school=school)


@school_bp.route('/team')
@login_required
def show_team():
    """
    显示某一个团队的相关信息 关系图
    :return:
    """
    pass
