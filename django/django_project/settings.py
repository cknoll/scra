"""
Django settings for django_project project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys

import deploymentutils as du


# DEVMODE should be False by default.
# Exceptions: 'runserver' command or explicitly set by ENV-Variable
# for  some management commands (on the production server) we want to explicitly switch off DEVMODE

# export DJANGO_DEVMODE=True; py3 manage.py <some_command>
env_devmode = os.getenv("DJANGO_DEVMODE")
if env_devmode is None:
    DEVMODE = "runserver" in sys.argv
else:
    DEVMODE = env_devmode.lower() == "true"


if os.getenv("SCRA_USE_EXAMPLE_CONFIG", "").lower() == "true":
    print(du.yellow("Note:"), "could not find `config.ini`. Using example file instead.")
    config = du.get_nearest_config("../deployment/config_example.ini", devmode=DEVMODE)
else:
    config = du.get_nearest_config("config1.ini", devmode=DEVMODE)


# this is where `manage.py` lives
DJANGO_BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# this is one level above
PROJECT_BASEDIR = os.path.dirname(DJANGO_BASEDIR)


SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

# prevent accidentally using DEBUG == "False" (which evaluates to `True`)
assert DEBUG in (True, False)
assert DEVMODE in (True, False)


BASEURL = config("BASEURL")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=config.Csv())


PATH_KNOWLEDGEBASE = config("PATH_KNOWLEDGEBASE").replace("__PROJECT_BASEDIR__", PROJECT_BASEDIR)
STATIC_ROOT = config("STATIC_ROOT").replace("__PROJECT_BASEDIR__", PROJECT_BASEDIR)

if 0:
    from ipydex import IPS, activate_ips_on_exception
    activate_ips_on_exception()
    IPS()
    1/0


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # for improved testing experience
    "django_nose",
    # to safely render HTML
    "django_bleach",
    # the example app
    "mainapp.apps.MainAppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(DJANGO_BASEDIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

SITE_ID = 1

BLEACH_ALLOWED_TAGS = [
    "p",
    "b",
    "i",
    "u",
    "em",
    "strong",
    "a",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "ul",
    "ol",
    "li",
    "pre",
    "code",
    "script",
    "span"
]


def allow_attributes(tag, name, value):
    """
    Use callable to decide which attributes we allow.
    Background: "script" should only be allowed for type="math/tex".

    see also: https://bleach.readthedocs.io/en/latest/clean.html#allowed-tags-tags
    """
    if name in ["href", "title", "style"]:
        return True
    elif tag == "script" and name == "type" and value.startswith("math/tex"):
        return True
    else:
        return False


BLEACH_ALLOWED_ATTRIBUTES = allow_attributes
BLEACH_ALLOWED_STYLES = ["color"]
BLEACH_STRIP_TAGS = False
BLEACH_STRIP_COMMENTS = False
