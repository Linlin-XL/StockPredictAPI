"""
Django settings for stock_api project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import environ
import logging
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    APP_ENV=(str, 'development'),
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(str, '127.0.0.1'),
    SQL_ENGINE=(str, 'django.db.backends.sqlite3'),
    POSTGRES_HOST=(str, 'localhost'),
    POSTGRES_DB=(str, BASE_DIR / "db.sqlite3"),
    POSTGRES_USER=(str, 'user'),
    POSTGRES_PASSWORD=(str, 'password'),
    POSTGRES_PORT=(str, '5432'),
)

# Load the environment configures
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

APP_ENV = os.environ.get("APP_ENV", env('APP_ENV'))
DEBUG = os.environ.get('DJANGO_DEBUG', env('DJANGO_DEBUG'))
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', env('DJANGO_ALLOWED_HOSTS')).split(" ")
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', env('DJANGO_SECRET_KEY'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'rest_framework',
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

ROOT_URLCONF = 'stock_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'stock_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", env("SQL_ENGINE")),
        "HOST": os.environ.get("POSTGRES_HOST", env("POSTGRES_HOST")),
        "NAME": os.environ.get("POSTGRES_DB", env("POSTGRES_DB")),
        "USER": os.environ.get("POSTGRES_USER", env("POSTGRES_USER")),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", env("POSTGRES_PASSWORD")),
        "PORT": os.environ.get("POSTGRES_PORT", env("POSTGRES_PORT")),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# PROD ONLY
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
