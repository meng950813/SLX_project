from flask import Blueprint, render_template
from flask_login import login_required


school_bp = Blueprint('school', __name__)


@school_bp.route('/<school>')
@login_required
def index(school):
    """
    显示该学校的所有学院和相关的信息 树图
    :param school:
    :return:
    """
    return render_template('school/index.html', school=school)


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
