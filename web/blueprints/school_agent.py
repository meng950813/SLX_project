from flask import Blueprint, render_template


school_agent_bp = Blueprint('school_agent', __name__)


@school_agent_bp.route('/')
@school_agent_bp.route('/homepage')
def homepage():
    """学校商务的个人主页"""
    return render_template('personal.html')


@school_agent_bp.route('/scholar/<int:teacher_id>')
def scholar_info(teacher_id):
    """专家个人信息"""
    return render_template('detail.html')
