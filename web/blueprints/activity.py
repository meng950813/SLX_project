import os
import datetime
from bson import ObjectId
from flask import Blueprint, render_template, current_app, send_from_directory, request, url_for, flash, Markup, abort
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
    添加活动的路由
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


@activity_bp.route('/manager')
@login_required
def manager():
    """
    浏览所有的活动
    :return:
    """
    activities = None
    try:
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        collection = mongo_operator.get_collection("activity")
        # 暂时获取所有的活动 并按照最后一次修改进行排序
        activities = collection.find({}, {'title': 1, 'date': 1, 'name': 1}).sort([('timestamp', -1)])
        activities = list(activities)
    except Exception as e:
        print('error when visiting activities: %s' % e)

    return render_template('activity/manager.html', activities=activities)


@activity_bp.route('/edit/<objectId>', methods=['GET', 'POST'])
@login_required
def edit(objectId):
    """
    编辑活动
    :return:
    """
    form = ActivityForm()
    try:
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        collection = mongo_operator.get_collection("activity")
        activity = collection.find_one({'_id': ObjectId(objectId)})
        # 检测用户是否可编辑
        if activity and activity['uid'] != current_user.id:
            abort(403)
        # 仅仅在GET下数据填充
        if request.method == 'GET':
            form.set_data(activity)

        if form.validate_on_submit():
            # 获取数据，并放入数据库中
            activity = form.get_data()
            # 放入最后一次编辑时间
            activity.update({'timestamp': datetime.datetime.now()})
            collection.update_one({'_id': ObjectId(objectId)}, {'$set': activity})
            flash('数据编辑成功', 'success')
            return redirect_back('activity.detail', objectId=objectId)
    except Exception as e:
        print("error when editing activity: %s" % e)
        flash('数据编辑失败,请稍后重试', 'danger')

    return render_template('activity/new_activity.html', form=form)


@activity_bp.route('/detail/<objectId>')
@login_required
def detail(objectId):
    """
    获取活动的具体
    :param objectId:
    :return:
    """
    activity = None
    try:
        mongo_operator = MongoOperator(**MongoDB_CONFIG)
        condition = {"_id": ObjectId(objectId)}
        activity = mongo_operator.get_collection('activity').find_one(condition)
        # 进行安全转义
        if 'content' in activity:
            activity['content'] = Markup(activity['content'])
    except Exception as e:
        print('error raised when viewing the detail of activity: %s' % e)

    if activity is None:
        abort(404)
    return render_template('activity/detail.html', activity=activity)


@activity_bp.route('/files/<path:filename>')
@login_required
def uploaded_files(filename):
    """
    根据文件名获取该文件的路由
    :param filename: 文件名成
    :return: 该文件的路由
    """
    path = os.path.join(basedir, current_app.config['IMAGE_SAVE_PATH'])
    return send_from_directory(path, filename)


@activity_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """
    flask-ckeditor上传图片时会用到这个路由，它会把图片保存在服务器并返回一个路由
    :return: 保存的文件的路由
    """
    f = request.files.get('upload')
    # TODO: 验证图片
    # TODO: 改变图片名称
    f.save(os.path.join(basedir, current_app.config['IMAGE_SAVE_PATH'], f.filename))
    url = url_for('.uploaded_files', filename=f.filename)
    return upload_success(url=url)
