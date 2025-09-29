from pathlib import Path
import os, json
import dj_database_url
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-ktfkhd0zkk(f8q_vzlivj(_xjx(gvu91t-%vl=6$ud+t2q$+o+'
SECRET_KEY = os.getenv("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
load_dotenv()
#DEBUG = True
DEBUG = os.getenv("DEBUG", "False") == "True"

TIME_ZONE = 'Asia/Manila'
USE_TZ = True


if os.getenv("RENDER"):  # when running on Render
    ALLOWED_HOSTS = ["sentinelsadmin.onrender.com"]
else:  # local development
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]



# Application definition
# /Users/jeremiahpantaras/Documents/sentinels-project/sentinels-a61ff-firebase-adminsdk-fbsvc-aaf9572a3f.json
# C:/Users/ASUS/Desktop/Thesis/sentinels-a61ff-firebase-adminsdk-fbsvc-35c84e60a7.json



AUTHENTICATION_BACKENDS = [
    'Login.auth_backend.HybridFacultyBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SentinelsProject',

    'Login',
    'Faculty',
    'SuperAdmin',
    'Student',
    
    'tailwind',
    'theme',
    'django_browser_reload',
]

TAILWIND_APP_NAME = 'theme'

NPM_BIN_PATH = "/usr/local/bin/npm"
# C:/Program Files/nodejs/npm.cmd
# /usr/local/bin/npm

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

ROOT_URLCONF = 'SentinelsProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'theme/templates'), os.path.join(BASE_DIR, 'SuperAdmin/templates'), os.path.join(BASE_DIR, 'Faculty/templates'), os.path.join(BASE_DIR, 'Student/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SentinelsProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Use DATABASE_URL if present (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback for local dev using .env
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'sentinels_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
#postgresql://sentinels_db_user:yAkAHRMXpXdOFOyqNSeTk0f2rAXj7gKd@dpg-d3d3tqjipnbc73failq0-a/sentinels_db
#
#POSTGRESQL DATABASE ON RENDER
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME', 'sentinels_db'),
#         'USER': os.getenv('DB_USER', 'postgres'),
#         'PASSWORD': os.getenv('DB_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '5432'),
#     }
# }
#DATABASE LOCALLY
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'sentinels_db',
#         'USER': 'postgres',
#         'PASSWORD': '!Poypoy.mignon!01',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'   # note the starting slash (important for production)

# Where collectstatic will put all static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Extra static files during development
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'theme/static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
