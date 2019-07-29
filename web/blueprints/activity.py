import os
import datetime
from flask import Blueprint, render_template, current_app, send_from_directory, request, url_for, flash
from flask_ckeditor import upload_success, upload_fail
from flask_login import login_required, current_user

from web.forms.activity import ActivityForm
from web.settings import basedir
from web.config import MongoDB_CONFIG
from web.utils.mongo_operator import MongoOperator
from web.utils import redirect_back


activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/', methods=['GET', 'POST'])
@login_required
def add_activity():
    """
    添加活动路由
    :return:
    """
    form = ActivityForm()
    # POST且验证通过
    if form.validate_on_submit():
        # 获取数据，并放入数据库中
        activity = form.get_data()
        # 放入作者和最后一次编辑时间
        activity.update({'uid': current_user.id, 'name': current_user.name, 'timestamp': datetime.datetime.now()})
        try:
            mongo_operator = MongoOperator(**MongoDB_CONFIG)
            collection = mongo_operator.get_collection("activity")
            collection.insert_one(activity)
            flash('活动写入成功', 'success')
            return redirect_back()
        except Exception as e:
            print("error when adding activity: %s" % e)
            flash('活动插入失败，请稍微重试', 'danger')

    return render_template('activity/new_activity.html', form=form)


@activity_bp.route('/files/<path:filename>')
@login_required
def uploaded_files(filename):
    path = os.path.join(basedir, current_app.config['IMAGE_SAVE_PATH'])
    return send_from_directory(path, filename)


@activity_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files.get('upload')
    # TODO: 验证图片
    # TODO: 改变图片名称
    f.save(os.path.join(basedir, current_app.config['IMAGE_SAVE_PATH'], f.filename))
    url = url_for('.uploaded_files', filename=f.filename)
    return upload_success(url=url)
