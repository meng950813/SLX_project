# SLX_project
## 1. Pycharm运行配置说明
因为flask的app对象被封装在了web/\__init__.py中的工厂方法create_app中，所以需要进行一些设置才可以运行
>1. 在Pycharm中对Flask server设置（可断点调试）：
>   1. 打开Edit Configuration
>   2. 设置Target type => Script path。
>   3. 设置Target => web/\__init__.py的完整路径。
>2. 在cmd中设置（无法断点调试）：
>   1. set FLASK_APP=web
>   2. flask run

以上的方法大致类似，flask的自动搜索机制会自动从FLASK_APP的值定义的模块中寻找名称为create_app()或make_app()的工厂函数
## 2. 第三方库
>1. Bootstrap-Flask:<br>
>该库是对bootstrap4的简单封装，提供了几个常用的宏(jinja中的函数)。
>官网:https://bootstrap-flask.readthedocs.io/en/latest/
>2. flask-wtf<br>
>flask-wtf是对form表单的封装，带有csrf令牌的安全表单。
>官网:http://www.pythondoc.com/flask-wtf/
## 3. 关于用户登录
>1. 登录目前使用到了mysql，对应的配置文件为web/config.py。
>2. 当用户登录成功后，会把该用户的用户名放入session['username']、uid放在session['uid']、type放在session['type']
>3. 当用户登录成功后，每一次刷新页面，程序都会从数据库中查询是否
>有自己的消息，如果有则显示，它已经注册到模板中，名称为unread_msg
## 4. 控制台输出
>程序输出尽量使用logging库，这样在使用docker部署服务器时可以docker logs [name] 直接观察到输出的内容(logging.warning及以上)
