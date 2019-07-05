from flask import Blueprint, render_template
from web.service.basic_info_service import search_teacher_basic_info


school_agent_bp = Blueprint('school_agent', __name__)


@school_agent_bp.route('/')
@school_agent_bp.route('/homepage')
def index():
    """学校商务的个人主页"""
    return render_template('personal.html')


@school_agent_bp.route('/scholar/<int:teacher_id>')
def scholar_info(teacher_id):
    """
    专家个人信息
    :param teacher_id:
    :return:
    """
    # 返回json 序列化后的文件
    teacher_basic_info = search_teacher_basic_info(teacher_id)
    length = [0, 0]

    # 计算该教师所拥有的基金的数目，并将其加到列表中，用以传送给前端
    if "funds" in teacher_basic_info:
        length[0] = len(teacher_basic_info["funds"])
    # 计算该教师所拥有的专利
    if "patent" in teacher_basic_info:
        length[1] = len(teacher_basic_info["patent"])

    return render_template('detail.html', teacher_basic_info=teacher_basic_info, length = length)


@school_agent_bp.route('/visit_record')
def visit_record():
    """拜访记录"""
    return render_template('visitRecode.html')


if __name__ == '__main__':
    scholar_info(73927)

