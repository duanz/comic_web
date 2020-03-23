
### 项目介绍

- 小说漫画爬虫项目，生产epub，推送至邮箱 
- 提供API和文档服务
- 搭配该项目```https://e.coding.net/duanxz/comic_admin_vue/comic_admin_vue.git```, 提供直观的后台管理操作
- 搭配该项目```https://e.coding.net/duanxz/comic_vue_app/comic_vue_app.git```, 提供简易的阅读器

### 软件环境

- python 3.7
- 数据库基于 MySQL 5.7

### 本地开发环境配置

- 克隆代码到本地：

  ``` bash
  git clone https://e.coding.net/duanxz/com_comic_web.git
  ```

- 创建数据库：
    ```sql
    CREATE DATABASE IF NOT EXISTS comic_web DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;
    ```

- 创建配置文件：

    创建 ```settings_local.py``` 文件，注意该文件与 ```comic_web/settings.py```在同一个目录中，或直接相关设置环境变量。

- 填写配置文件```settings_local.py```：

  ``` python

    import os

    # 数据库配置
    os.environ["MYSQL_HOST"] = "localhost"  # 数据库服务器地址
    os.environ["MYSQL_USER"] = "root"   # 数据库用户名
    os.environ["MYSQL_PORT"] = "3306"   # 数据库端口
    os.environ["MYSQL_PASSWORD"] = "123456" # 数据库密码
    os.environ["REDIS_SERVER"] = "redis://127.0.0.1:7777/2" #   redis服务

    # 系统相关配置
    os.environ['APP_HOST'] = "localhost"    # 项目地址
    os.environ['PRODUCTION_MODE'] = ""    # 该配置项表示以debug模式运行
    os.environ['UPLOAD_SAVE_PATH'] = ""    # 上传文件保存目录
    os.environ['UPLOAD_STATIC_URL'] = ""    # 上传文件访问目录

    # 邮箱配置 网易163邮箱为例
    os.environ["EMAIL_HOST"] = "smtp.163.com"
    os.environ["EMAIL_PORT"] = "25"
    os.environ["EMAIL_HOST_USER"] = "your@163.com"
    os.environ["EMAIL_HOST_PASSWORD"] = "*********"
    os.environ["EMAIL_FROM_EMAIL"] = "comic_web<your@163.com>"
    os.environ["EMAIL_TO_EMAIL"] = "your@kindle.cn, my@kindle.cn"
  ```

- 安装依赖：
  
  进入requirements.txt所在目录，执行 ```pip install -r requirements.txt```
  
  拉取生成EPUB工具```https://github.com/anqxyr/mkepub.git```,并安装```python setup.py build```, ```python setup.py install```

- 迁移数据:
    1. ```python manage.py makemigrations```
    2. ```python manage.py migrate```
- 创建django超级管理员:

    ```python manage.py createsuperuser```

- 启动服务器:

    ```python manage.py runserver``` ，即可在本地访问 http://127.0.0.1:8000
    ```celery beat -A comic_web -l info```
    ```celery -A comic_web worker -l info```, 启动celery执行任务

    - 使用说明：
        1. 管理后台入口：```http://127.0.0.1:8000/admin```
        3. 在线API文档入口：```http://127.0.0.1:8000/api-docs/```
