"""
Django settings for comic_web project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from mongoengine import connect as MongoConnect
import comic_web.settings_local

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k11&%-cuo^ovxx*8_0hsr0r9b17r&&)_be!0pmz+_4v7v(-bj5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

APP_HOST = os.getenv('APP_HOST')

# 上传文件保存目录
UPLOAD_SAVE_PATH = os.getenv('UPLOAD_SAVE_PATH', os.path.join(
    BASE_DIR, 'static', 'mall_web_upload'))
# 上传文件访问目录
UPLOAD_STATIC_URL = os.getenv('UPLOAD_STATIC_URL', '/static/mall_web_upload/')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'comic_admin',
    'book_admin',
    'members',
    'rest_framework',
    'django_filters',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'django_crontab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'comic_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  # jinja2模版
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # 模版文件位置
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'comic_web.jinja2_env.environment',  # XXX为你的app名称,
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'comic_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'comic_web',
        'USER': os.getenv('MYSQL_USER', 'duan'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', '123456'),
        'HOST': os.getenv('MYSQL_HOST', 'localhost'),
        'PORT': 27017,
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'NON_FIELD_ERRORS_KEY': 'details'
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'auth.User'

# 定时任务
CRONJOBS = [
    # 表示每分钟执行一次
    ('*/1 * * * *', 'comic_admin.workers.spiders.work.task', '>>{}/name.log'.format(UPLOAD_SAVE_PATH))
]

# 默认分页数量
PAGINATE_BY = 30

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures',),)


# 需添上正确的参数
# TODO
WX_CONF = {
    'AppID': os.getenv('WX_APP_ID', 'root'),
    'AppSecret': os.getenv('WX_APP_SECRET', 'root'),
    'MiniAppID': os.getenv('WX_MINI_APP_ID', 'root'),
    'MiniAppSecret': os.getenv('WX_MINI_APP_SECRET', 'root'),
    'MchID': os.getenv('MCH_ID', 'root'),
    'MchKey': os.getenv('MCH_KEY', 'root'),
    'NotifyUrl': '',
    'AppHost': os.getenv('APP_HOST', 'localhost'),
    'EventApiToken': os.getenv('WX_EVENT_API_TOKEN', 'root'),
}
