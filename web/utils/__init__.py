from flask import current_app, request, url_for, redirect
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from urllib.parse import urljoin, urlparse

from web.settings import Operations


def generate_token(user_id, operation, expire_in=None, **kwargs):
    """
    生成令牌
    :param user_id: 用户的user id
    :param operation: 目前进行的操作
    :param expire_in: 过期时间
    :param kwargs:
    :return:
    """
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user_id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    """
    验证令牌，成功后会对数据进行操作，并提交
    :param user:
    :param token:
    :param operation:
    :param new_password:
    :return:
    """
    s = Serializer(current_app.config['SECRET_KEY'])

    # 尝试解析数据
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False
    # 需要存在两个键
    if operation != data.get('operation') or user.id != data.get('id'):
        return False
    # 重置密码
    if operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    # 改变邮箱
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        user.email = new_email
    else:
        return False
    # 数据库修改
    return True


def is_safe_url(target):
    """保证域名相同"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='school_agent.index', **kwargs):
    """
    返回上一页面
    :param default:
    :param kwargs:
    :return:
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
