# Django settings for subnets project.

RunningOn = 'dev_at_QM'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('David Pick', 'D.M.Pick@qmul.ac.uk'),
)

MANAGERS = ADMINS

if RunningOn == 'dungbeetle':
    DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'subnets'             # Or path to database file if using sqlite3.
    DATABASE_USER = 'subnets'             # Not used with sqlite3.
    DATABASE_PASSWORD = '3U2z1BZ2'         # Not used with sqlite3.
    DATABASE_HOST = 'mysql5.qmul.ac.uk'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
elif RunningOn == 'dev_at_QM':
    DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = '/home/jasonl/svn/subnets/Database/database.db' # Or path to database file if using sqlite3.		
    DATABASE_USER = ''             # Not used with sqlite3.
    DATABASE_PASSWORD = ''         # Not used with sqlite3.
    DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
elif RunningOn == 'dev_at_home':
    DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = '/home/jason/Projects/qm_projects/subnets/Database/database.db'  # Or path to database file if using sqlite3.		
    DATABASE_USER = ''             # Not used with sqlite3.
    DATABASE_PASSWORD = ''         # Not used with sqlite3.
    DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/django/django_projects/subnets/Media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://subnets.core-net.qmul.ac.uk/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'wko0telssmkebd^)f&a3jbrooqgt17p@#%sorb&9(b#m4wqf**'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

if RunningOn == 'dungbeetle':
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_IdCheck.auth.middleware.IdCheckMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

ROOT_URLCONF = 'subnets.urls'

if RunningOn == 'dungbeetle':
	TEMPLATE_DIRS = (
	    '/home/django/django_projects/subnets/Template',
	    '/home/django/django_projects/subnets/Template/dhcp',
	    '/home/django/django_projects/subnets/Template/dns',
	    '/home/django/django_projects/subnets/Template/history',
	)
elif RunningOn  == 'dev_at_home':
	TEMPLATE_DIRS = (
	    #work from home
	    '/home/jason/Projects/qm_projects/subnets/Template',
	    '/home/jason/Projects/qm_projects/subnets/Template/dhcp',
	    '/home/jason/Projects/qm_projects/subnets/Template/dns',
	    '/home/jason/Projects/qm_projects/subnets/Template/history',
	)
elif RunningOn == 'dev_at_QM':
	TEMPLATE_DIRS = (
		#work from qm
		'/home/jasonl/svn/subnets/Template',
		'/home/jasonl/svn/subnets/Template/dhcp',
		'/home/jasonl/svn/subnets/Template/dns',
		'/home/jasonl/svn/subnets/Template/history',
		    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
		    # Always use forward slashes, even on Windows.
		    # Don't forget to use absolute paths, not relative paths.
	)

<<<<<<< HEAD
ROOT_URLCONF = 'mynet.urls'

TEMPLATE_DIRS = (
	#work from home
	'/home/jason/Projects/qm_projects/mynet/Template',
	'/home/jason/Projects/qm_projects/mynet/Template/dhcp',
	'/home/jason/Projects/qm_projects/mynet/Template/dns',
	'/home/jason/Projects/qm_projects/mynet/Template/history',
	#work from qm
	#'/home/jasonl/svn/mynet/Template',
	#'/home/jasonl/svn/mynet/Template/dhcp',
	#'/home/jasonl/svn/mynet/Template/dns',
	#'/home/jasonl/svn/mynet/Template/history',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
=======
>>>>>>> 209bca9c28ac331be452231249a280608d85cf5d
INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.admin',
	'subnets.AccessControl',
	'subnets.DNS',
	'subnets.DHCP',
	'subnets.DHCP.templatetags.paginator',
	'subnets.HistoryLog',
	'subnets.NetaddrTest',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_IdCheck.auth.backends.IdCheckBackend',
)
