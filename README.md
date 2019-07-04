
# SLX_project
## 1. Pycharm运行配置说明
因为flask的app对象被封装在了web/\__init__.py中的工厂方法create_app中，所以需要进行一些设置才可以运行
>1. 在Pycharm中对Flask server设置（可断点调试）：
>   1. 打开Edit Configuration
>   2. 设置Target type => Script path。
>   2. 设置Target => web/\__init__.py的完整路径。
>2. 在cmd中设置（无法断点调试）：
>   1. set FLASK_APP=web
>   2. flask run

以上的方法大致类似，flask的自动搜索机制会自动从FLASK_APP的值定义的模块中寻找名称为create_app()或make_app()的工厂函数
