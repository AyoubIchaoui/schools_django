# Django settings for bitpoint project.
import sys
import os

DEBUG = True


ADMINS = (
    # ('AIbrahim', 'abdulrasheedibrahim47@gmail.com'),
)

MANAGERS = ADMINS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PROJECT_DIR = os.path.join(BASE_DIR, os.pardir)

TENANT_APPS_DIR = os.path.join(PROJECT_DIR, os.pardir)
sys.path.insert(0, TENANT_APPS_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'railway',               
        'USER': 'postgres',
        'PASSWORD': 'iCygpgmoyhlnTglsIuKXmgQrpKSIipPT',
        'HOST': 'interchange.proxy.rlwy.net',
        'PORT': '24169',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Africa/Lagos'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

with open(BASE_DIR + '/key/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

# List of callables that know how to import templates from various sources.

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


MIDDLEWARE = (
    'bitpoint.middleware.BitpointTenantMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')

        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'bitpoint.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'main_site.urls_site_admin'
ADMIN_URLCONF = 'main_site.urls_site_admin'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bitpoint.wsgi.application'


SHARED_APPS = (
    'django_tenants',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'schools',
    'authentication',
    'main_site',
    'session_security',
    'markdownx',
)

TENANT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'authentication',
    'pwa',
    'sms',
    'frontend',
    'session_security',
)

TENANT_MODEL = "schools.Client"  # app.Model

TENANT_DOMAIN_MODEL = "schools.Domain"  # app.Model

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

AUTH_USER_MODEL = 'authentication.User'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

INSTALLED_APPS = list(set(SHARED_APPS + TENANT_APPS))

# session conf
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_WARN_AFTER = 300

# Time before the user should be logged out if inactive
SESSION_SECURITY_EXPIRE_AFTER = 600

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DEFAULT_FILE_STORAGE = "django_tenants.files.storage.TenantFileSystemStorage"
MULTITENANT_RELATIVE_MEDIA_ROOT = "uploaded_files"

# service worker
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'sms/static/js', 'serviceworker.js')

# Mail CONF
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

with open(BASE_DIR + '/key/sendgrid_api_key.txt') as f:
    SENDGRID_API_KEY = f.read().strip()