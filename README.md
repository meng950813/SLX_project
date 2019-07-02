# SLX_project
##1. Pycharm运行配置说明
因为flask的app对象被封装在了web/\__init__.py中的工厂方法create_app中，所以需要在Pycharm中对Edit Configuration中设置：
>1. Target type => Script path。
>2. Target => web/\__init__.py的完整路径。