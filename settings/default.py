from funfactory.settings_base import *

SYSLOG_TAG = "http_app_reporter"

DATABASE_ROUTERS = ('website_issues.db.DatabaseRouter',
                    'multidb.MasterSlaveRouter',)

CACHE_DEFAULT_PERIOD = CACHE_MIDDLEWARE_SECONDS = 60 * 5  # 5 minutes
CACHE_COUNT_TIMEOUT = 60  # seconds
CACHE_PREFIX = CACHE_MIDDLEWARE_KEY_PREFIX = 'reporter:'

# Site ID.
# Site 1 is the desktop site, site == MOBILE_SITE_ID is the mobile site. This
# is set automatically in input.middleware.MobileSiteMiddleware according to
# the request domain.
DESKTOP_SITE_ID = 1
MOBILE_SITE_ID = 2
# The desktop version is the default.
SITE_ID = DESKTOP_SITE_ID

# Accepted locales
PROD_LANGUAGES = ('ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en-US', 'es',
                   'fr', 'fy-NL', 'ga-IE', 'gl', 'he', 'hr', 'hu', 'id', 'it',
                   'ja', 'ko', 'nb-NO', 'nl', 'pl', 'pt-BR', 'pt-PT', 'ro',
                   'ru', 'sk', 'sl', 'sq', 'uk', 'vi', 'zh-TW', 'zh-CN')
RTL_LANGUAGES = ('ar', 'he',)  # ('fa', 'fa-IR')
# Fallbacks for locales that are not recognized by Babel. Bug 596981.
BABEL_FALLBACK = {'fy-nl': 'nl'}

LANGUAGE_URL_MAP = dict((i[:2], i) for i in PROD_LANGUAGES if '-' in i)
LANGUAGE_URL_MAP.update((i.lower(), i) for i in PROD_LANGUAGES)

# Paths that don't require a locale prefix.
SUPPORTED_NONLOCALES = ('media', 'admin')

# Templates
CSRF_FAILURE_VIEW = '%s.urls.handler_csrf' % os.path.basename(ROOT)

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    # TODO: is this needed?
    'input.context_processors.i18n',
    'input.context_processors.input',
    'input.context_processors.mobile',
    'input.context_processors.opinion_types',

    'search.context_processors.product_versions',
    'jingo_minify.helpers.build_ids',
]

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the jingo-minify app.
MINIFY_BUNDLES = {
    'css': {
        'common': (
            'css/libs/reset-min.css',
            'css/libs/jquery-ui.css',
            'css/input.css',
        ),
        'common_mobile': (
            'css/libs/reset-min.css',
            'css/input-mobile.css',
        ),

        # old styles for submission pages
        'common_old': (
            'css/reporter.css',
        ),
        'mobile_old': (
            'css/reporter.css',
            'css/mobile.css',
        ),

        'feedback': (
            'css/libs/reset2.css',
            'css/feedback.css',
        ),
        'feedback-mobile': (
            'css/libs/reset-min.css',
            'css/feedback-mobile.css',
        ),
    },
    'js': {
        'common': (
            # Google analytics
            'js/analytics.js',

            'js/libs/jquery.min.js',
            'js/libs/jquery-ui.min.js',
            'js/libs/jquery.cookie.js',
            'js/init.js',
            'js/input.js',
            'js/search.js',

            # Time-based charts
            'js/libs/highcharts.src.js',
            'js/dashboard.js',
        ),
        'common_mobile': (
            'js/libs/jquery.min.js',
            'js/input-mobile.js',
        ),

        # old scripts for submission pages (desktop and mobile)
        'common_old': (
            'js/libs/jquery.min.js',
            'js/libs/jquery.NobleCount.js',
            'js/init.js',
            'js/reporter.js',
        ),

        # Release versions feedback
        'feedback': (
            # Google analytics
            'js/analytics.js',

            'js/libs/jquery.min.js',
            'js/init.js',
            'js/feedback.js',
        ),
        'feedback-mobile': (
            # Google analytics
            'js/analytics.js',

            'js/feedback-mobile.js',
        ),
    },
}
JAVA_BIN = '/usr/bin/java'

JINGO_EXCLUDE_APPS = ['debug_toolbar', 'admin', 'adminplus']

MIDDLEWARE_CLASSES = get_middleware(
    append=(
        'input.middleware.MobileSiteMiddleware',
        'commonware.response.middleware.GraphiteMiddleware',
        'commonware.response.middleware.GraphiteRequestTimingMiddleware',
    )
)

INSTALLED_APPS = get_apps(
    append=(
        'common',  # comes first so it always takes precedence.
        'input',  # comes first so it always takes precedence.

        'api',
        'feedback',
        'myadmin',
        'search',
        'themes',
        'website_issues',

        'commonware',
        'annoying',
        'cronjobs',
        'haystack',  # for search
        'celery_haystack',  # for lazy indexing
        'adminplus',
        'jingo_minify',

        'django.contrib.admin',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ),
    exclude=(
        'django_sha2',
        'django_browserid',
        'compressor',
    )
)

# Where to store product details
PROD_DETAILS_DIR = path('lib/product_details_json')

# Term filter options
MIN_TERM_LENGTH = 3
MAX_TERM_LENGTH = 25

# Number of items to show in the "Trends" box and Messages box.
MESSAGES_COUNT = 10
TRENDS_COUNT = 10

# Sphinx Search Index
SPHINX_HOST = '127.0.0.1'
SPHINX_PORT = 3314
SPHINXQL_PORT = 3309
SPHINX_SEARCHD = 'searchd'
SPHINX_INDEXER = 'indexer'
SPHINX_CATALOG_PATH = path('tmp/data/sphinx')
SPHINX_LOG_PATH = path('tmp/log/searchd')
SPHINX_CONFIG_PATH = path('configs/sphinx/sphinx.conf')

TEST_SPHINX_PORT = 3414
TEST_SPHINXQL_PORT = 3409
TEST_SPHINX_CATALOG_PATH = path('tmp/test/data/sphinx')
TEST_SPHINX_LOG_PATH = path('tmp/test/log/searchd')

SEARCH_MAX_RESULTS = 1000
SEARCH_PERPAGE = 20  # results per page
SEARCH_MAX_PAGES = SEARCH_MAX_RESULTS / SEARCH_PERPAGE

CLUSTER_SIM_THRESHOLD = 2

## Celery
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "input"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
CELERY_IMPORTS = ('django_arecibo.tasks',)

## API
TSV_EXPORT_DIR = path('media/data')

# URL for reporting arecibo errors too. If not set, won't be sent.
ARECIBO_SERVER_URL = ""

## ElasticSearch
ES_HOSTS = []
ES_INDEX = 'input'
ES_DISABLED = True
## FEATURE FLAGS:
# Setting this to False allows feedback to be collected from any user agent.
# (good for testing)
ENFORCE_USER_AGENT = True
DISABLE_TERMS = False

# Minnum of opinions in the last 30 days for version to be shown in dashboard
DASHBOARD_THRESHOLD = 800
DASHBOARD_THRESHOLD_MOBILE = 120
SESSION_COOKIE_SECURE = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'input',
    },
}

STATIC_ROOT = 'static'
STATIC_URL = '/static/'

# Override this from funfactory.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

# There isn't a funfactory helper for this.
STATICFILES_FINDERS = tuple(finder for finder in STATICFILES_FINDERS
    if finder not in ('compressor.finders.CompressorFinder',))
