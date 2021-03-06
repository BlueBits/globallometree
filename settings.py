# -*- coding: utf-8 -*-
# Django settings for globallometree project.

import os.path
gettext = lambda s: s

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', 'English'),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(BASE_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
#    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_PATH, 'templates'),
)

CMS_TEMPLATES = (
    ('cms/basic_page.html', 'CMS basic page'),
    ('cms/home_page.html', 'CMS home page'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    #'grappelli',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'haystack',
    'apps.data',
    'apps.accounts',
    'apps.journals',
    'gunicorn',
    'south',
    'cms',
    'mptt',
    'sekizai',
    'cms.plugins.file',
    'cms.plugins.link',
    'cms.plugins.picture',
    'cms.plugins.text',
    'cms.plugins.teaser',
    'plugins.linkbox',
    'crispy_forms',
)

CRISPY_TEMPLATE_PACK = 'bootstrap'

# Override the server-derived value of SCRIPT_NAME 
# See http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#lighttpdfastcgiandothers
FORCE_SCRIPT_NAME = ''

#Static files configuration
STATIC_ROOT = os.path.join(BASE_PATH, 'static_collected')
STATIC_URL = '/static/'

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'globallometree',
    },
}

#Encoding used for export and import of data
DATA_EXPORT_ENCODING = 'cp1252'
DATA_EXPORT_ENCODING_NAME = 'Windows-1252'

if os.path.exists(os.path.join(BASE_PATH, 'prod')):
    STAGE = 'prod'
    INITIAL_DATA_DIR = '/opt/apps/globallometree_initial_data/'
    from settings_deployment import *
else:
    STAGE = 'dev'
    try:
        from settings_local import *
    except Exception as e:
        print "Failed to import settings_local. Copy ./bootstrap/settings_local.example.py to ./settings_local.py"
        print "The error was %s" % e    


try:
    from settings_secret import *
except:
    print "Skipping settings_secret.py since the file does not exist"
