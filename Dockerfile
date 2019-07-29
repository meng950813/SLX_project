FROM python:3.7

VOLUME ['/code']
WORKDIR /code
# 复制requirements.txt
COPY requirements.txt /code

# 安装gunicorn代替测试服务器
RUN pip install -r requirements.txt && pip install gunicorn
#设置环境变量
EXPOSE 5000
CMD gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app
