"""
author: xiaoniu
date: 2019-03-14
desc: 简单提供了数据库常用的语句
"""
import pymysql
import logging
from DBUtils.PooledDB import PooledDB

POOL = None


class DBError(Exception):
    pass


def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    """
    初始化全局变量engine,仅仅需要初始化一次即可
    :param user: 数据库用户名
    :param password: 数据库密码
    :param database: 使用哪个数据库
    :param host: 数据库域名
    :param port: 数据库端口
    :param kw: 额外参数
    :return: None
    """
    global POOL
    if POOL is not None:
        raise DBError('Engine is already initialized')

    params = dict(host=host, user=user, password=password, database=database, port=port)
    # 数据库打开的默认值
    defaults = dict(use_unicode=True, autocommit=False)
    # 尝试覆盖默认值
    for k, v in defaults.items():
        params[k] = kw.pop(k, v)
    # 更新其他值
    params.update(kw)

    POOL = PooledDB(
        creator=pymysql,  # 使用pymysql连接数据库
        maxconnections=6,  # 连接池允许的最大连接数目，为0或None时表示不限制连接数目
        mincached=2,  # 初始化时连接池的最少空闲链接
        blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待，为False则报错
        maxusage=None,  # 一个连接最多被复用的次数
        setsession=[],  # 开始会话前执行的命令列表
        ping=0,
        **params
    )
    # output
    logging.info('Init mysql engine ok.')


def _select(sql, first, *args):
    """
    select语句
    :param sql: SQL语句 内部变量使用?
    :param first: 是否只获取一个
    :param args: SQL语句中要使用的变量
    :return: 返回查询的结果
    """
    global POOL
    connection = None
    cursor = None
    logging.info('SQL: %s %s' % (sql, args if len(args) > 0 else ""))
    sql = sql.replace('?', '%s')

    try:
        connection = POOL.connection()
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        # 利用本身的 execute 函数的特性，传入两个参数：sql语句与tuple类型的参数，以避免sql注入
        cursor.execute(sql, args)

        if first:
            result = cursor.fetchone()
            return result
        else:
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def select_one(sql, *args):
    """
    执行select SQL语句并返回dict结构的结果或None
    :param sql:select的SQL语句，包含?
    :param args:select的SQL语句所对应的值
    :return: dict结构的一个结果或者None
    """
    return _select(sql, True, *args)


def select(sql, *args):
    """
    执行SQL语句
    :param sql:  select的SQL语句，可含?
    :param args: select的SQL语句所对应的值
    :return: list(dict) 或者None
    """
    return _select(sql, False, *args)


def _insert(sql, insert_many, args):
    """
    insert语句
    :param sql: SQL语句 内部变量使用?
    :param insert_many: 是否要插入多行
    :param args: SQL语句中要使用的变量
    :return: 返回插入的结果
    """
    global POOL
    connection = None
    cursor = None
    logging.info('SQL: %s %s' % (sql, args if len(args) > 0 else ""))
    sql = sql.replace('?', '%s')

    try:
        connection = POOL.connection()
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

        # print('SQL: %s %s' % (sql, args if len(args) > 0 else ""))

        # 利用本身的 execute 函数的特性，传入两个参数：sql语句与tuple类型的参数，以避免sql注入
        if insert_many:
            # 插入多行
            cursor.executemany(sql, args)
        else:
            cursor.execute(sql, args)

        # 返回最后插入行的主键ID
        return cursor.lastrowid

    except Exception as e:
        print(e)
        connection.rollback()  # 事务回滚

    finally:
        cursor.close()

        connection.commit()

        connection.close()


def insert(sql, args):
    """
    执行SQL语句
    :param sql:  insert的SQL语句，可含?
    :param args: insert的SQL语句所对应的值
    :return: 最后插入行的主键ID
    """
    return _insert(sql, False, args)


def insert_many(sql, *args):
    """
    执行SQL语句
    :param sql:  insert的SQL语句，可含?
    :param args: insert的SQL语句所对应的值
    :return: 最后插入行的主键ID
    """
    return _insert(sql, True, *args)


def _update(sql, *args):
    """
    select语句
    :param sql: SQL语句 内部变量使用?
    :param args: SQL语句中要使用的变量
    :return: 返回
    """
    global POOL
    connection = None
    cursor = None
    logging.info('SQL: %s %s' % (sql, args if len(args) > 0 else ""))
    sql = sql.replace('?', '%s')
    row_count = 0

    try:
        connection = POOL.connection()
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        # 利用本身的 execute 函数的特性，传入两个参数：sql语句与tuple类型的参数，以避免sql注入
        cursor.execute(sql, args)
        # 获取影响的行
        row_count = cursor.rowcount
        connection.commit()
    except Exception as e:
        connection.rollback()
        print("db operation error is : ",e)
    finally:
        cursor.close()
        connection.close()
    return row_count


def update(sql, *args):
    """
    执行SQL语句
    :param sql:  SQL语句，可含?
    :param args: select的SQL语句所对应的值
    :return: 返回受影响的行数
    """
    return _update(sql, *args)


if __name__ == '__main__':
    import sys

    sys.path.append("..")

    from web.config import DB_CONFIG

    # 需要预先调用，且只调用一次
    create_engine(**DB_CONFIG)

    teachers = select('select * from es_teacher limit 0,10')
    # print(teachers)

    # sql_base = "select * from sys_user where NAME = %s"
    # print(select( sql_base % "1 or 1=1 or %s","123") )

    # print(select( sql_base, "%测试账号" ))

    # 测试插入语句
    # sql_base = """insert into sys_net_of_school_agent
    #         (U_ID,TEACHER_ID,TEACHER_NAME,COLLEGE_ID,COLLEGE_NAME,SCHOOL_ID,SCHOOL_NAME,REMARK,LINK)
    #         value(%(user_id)s,%(teacher_id)s,%(teacher_name)s,%(college_id)s,%(college_name)s,%(school_id)s,%(school_name)s,%(remark)s,%(link_method)s)"""

    # info = (100000, 73930, "张晖", 1355, "马克思主义学院", 19024, "中国农业大学", "备注，dd", "12345678908")
    # info_dict = {
    #     "user_id": 100000,
    #     "teacher_id": 73994,
    #     "teacher_name": "谢光辉",
    #     "college_id": 1341,
    #     "college_name": "农学院",
    #     "school_id": 19024,
    #     "school_name": "中国农业大学",
    #     "remark": "备注-  33",
    #     "link_method": "123@123.com"
    # }
    # print(insert(sql_base, info_dict))

    # 测试更新语句
    sql_temp = 'update sys_net_of_school_agent set TEACHER_ID = ? where TEACHER_NAME=?'
    print('修改成功' if update(sql_temp, 100, '崇志宏') == 1 else '修改失败')