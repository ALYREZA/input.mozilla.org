import datetime
import json
import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.feedgenerator import Atom1Feed

import commonware.log
import jingo
from product_details.version_compare import Version
from tower import ugettext as _, ugettext_lazy as _lazy

from input import (PRODUCTS, PRODUCT_IDS, FIREFOX, LATEST_BETAS,
                   OPINION_PRAISE, OPINION_ISSUE, OPINION_IDEA, OPINION_TYPES)
from input.decorators import cache_page, forward_mobile
from input.urlresolvers import reverse
from search.client import Client, SearchError
from search.forms import ReporterSearchForm, PROD_CHOICES, VERSION_CHOICES

log = commonware.log.getLogger('i.search')


unixtime = lambda s: int(time.mktime(time.strptime(s, '%Y-%m-%d')))


def _get_results(request, meta=[], client=None):
    form = ReporterSearchForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        query = data.get('q', '')
        product = data.get('product') or request.default_prod.short
        version = data.get('version')
        search_opts = _get_results_opts(request, data, product, meta)
        type_filter = search_opts['type'] if 'type' in search_opts else None
        c = client or Client()
        opinions = c.query(query, **search_opts)
        metas = c.meta
    else:
        opinions = []
        type_filter = None
        product = request.default_prod
        query = ''
        version = (getattr(product, 'default_version', None) or
                   Version(LATEST_BETAS[product]).simplified)
        metas = {}

    product = PRODUCTS.get(product, FIREFOX)

    return (opinions, form, product, version, metas, type_filter)


def _get_results_opts(request, data, product, meta=[]):
    """Prepare the search options for the Sphinx query"""
    search_opts = data
    search_opts['product'] = PRODUCTS[product].id
    search_opts['meta'] = meta
    search_opts['offset'] = ((data.get('page', 1) - 1) *
                             settings.SEARCH_PERPAGE)

    sentiment = data.get('sentiment', '')
    if sentiment == 'happy':
        search_opts['type'] = OPINION_PRAISE.id
    elif sentiment == 'sad':
        search_opts['type'] = OPINION_ISSUE.id
    elif sentiment == 'ideas':
        search_opts['type'] = OPINION_IDEA.id

    return search_opts


def get_sentiment(data=[]):
    r = dict(happy=0, sad=0, ideas=0, sentiment='happy')

    for el in data:
        if el['type'] == OPINION_PRAISE.id:
            r['happy'] = el['count']
        elif el['type'] == OPINION_ISSUE.id:
            r['sad'] = el['count']
        elif el['type'] == OPINION_IDEA.id:
            r['ideas'] = el['count']

    r['total'] = r['sad'] + r['happy'] + r['ideas']

    if r['sad'] > r['happy']:
        r['sentiment'] = 'sad'

    return r


class SearchFeed(Feed):
    # TODO(davedash): Gracefully degrade for unavailable search.
    feed_type = Atom1Feed

    author_name = _lazy('Firefox Input')
    subtitle = _lazy("Search Results in Firefox Beta Feedback.")

    def get_object(self, request):
        data = dict(opinions=_get_results(request)[0], request=request)
        return data

    def link(self, obj):
        """Global feed link. Also used as GUID."""
        return u'%s?%s' % (reverse('search'),
                           obj['request'].META['QUERY_STRING'])

    def title(self, obj):
        """Global feed title."""
        request = obj['request']
        query = request.GET.get('q')

        # L10n: This is the title to the Search ATOM feed.
        return (_(u"Firefox Input: '{query}'").format(query=query) if query
                else _('Firefox Input'))

    def items(self, obj):
        """List of comments."""
        return obj['opinions'][:settings.SEARCH_PERPAGE]

    def item_categories(self, item):
        """Categorize comments. Style: "product:firefox" etc."""
        categories = {
            'product': PRODUCT_IDS.get(item.product).short,
            'version': item.version,
            'platform': item.platform,
            'locale': item.locale,
            'sentiment': item.type.short
        }

        return (':'.join(i) for i in categories.items())

    def item_description(self, item):
        """A comment's main text."""
        return item.description

    def item_link(self, item):
        """Permalink per item. Also used as GUID."""
        return item.get_url_path()

    def item_pubdate(self, item):
        """Publishing date of a comment."""
        return item.created

    def item_title(self, item):
        """A comment's title."""
        return unicode(item)


# TODO(davedash): use a bound form for defaults in views and get rid of this.
def get_defaults(form):
    """
    Keep form data as default options for further searches, but remove page
    from defaults so that every parameter change returns to page 1.
    """
    return dict((k, v) for k, v in form.data.items()
                if k != 'page' and k in form.fields)


def get_period(form):
    """Determine date period chosen."""
    days = 0

    if not getattr(form, 'cleaned_data', None):
        return None, days

    d = form.cleaned_data
    start = d.get('date_start')
    end = d.get('date_end') or datetime.date.today()

    if not (start and end):
        return 'infin', days

    _ago = lambda x: datetime.date.today() - datetime.timedelta(days=x)
    days = (end - start).days

    if (end == datetime.date.today() and start):
        return {_ago(1): '1d',
                _ago(7): '7d',
                _ago(30): '30d'}.get(start, 'custom'), days

    return 'custom', days


@forward_mobile
@cache_page(use_get=True)
def index(request):
    """
    Display search results for Opinions on Firefox. Shows breakdown of
    Praise/Issues/Ideas, sites/themes, and search filters.

    If no search criteria are explicitly set, the page is considered the
    "Dashboard" (i.e. the home page of Firefox Input). Otherwise, the title
    of the page is "Search Results".
    """

    try:
        meta = ('type', 'locale', 'platform', 'day_sentiment', 'manufacturer',
                'device')
        (results, form, product, version, metas, type_filter) = _get_results(
                request, meta=meta)
    except SearchError, e:
        return jingo.render(request, 'search/unavailable.html',
                           {'search_error': e}, status=500)

    page = form.data.get('page', 1)

    # Get the desktop site's absolute URL for use in the settings tab
    desktop_site = Site.objects.get(id=settings.DESKTOP_SITE_ID)

    data = dict(
        # No form data means we're on the "dashboard".
        dashboard=(not form.data),
        desktop_url='http://' + desktop_site.domain,
        form=form,
        product=product,
        products=PROD_CHOICES,
        version=dict(form.fields['version'].choices).get(version or '--'),
        versions=VERSION_CHOICES[product],
    )

    # Check to see if this is the user's first visit to a search page
    # (usually the dashboard/home page). We'll show them a welcome
    # message if they don't have a "seen_welcome" flag in their session.
    data['seen_welcome'] = request.session.get('seen_welcome', False)
    if not data['seen_welcome']:
        request.session['seen_welcome'] = True

    data['period'], days = get_period(form)

    if results:
        pager = Paginator(results, settings.SEARCH_PERPAGE)
        data['opinion_count'] = pager.count
        # If page request (e.g., 9999) is out of range, deliver last page of
        # results.
        try:
            data['page'] = pager.page(page)
        except (EmptyPage, InvalidPage):
            data['page'] = pager.page(pager.num_pages)

        data['opinions'] = data['page'].object_list
        data['sent'] = get_sentiment(metas.get('type', {}))
        data['demo'] = dict(locale=metas.get('locale'),
                            platform=metas.get('platform'),
                            manufacturer=metas.get('manufacturer'),
                            device=metas.get('device'))
        if days >= 7 or data['period'] == 'infin':
            daily = metas.get('day_sentiment', {})
            if type_filter:
                opinion = OPINION_TYPES[type_filter]
                chart_data = dict(series=[dict(name=unicode(opinion.pretty),
                        data=daily[opinion.short])])
            else:
                chart_data = dict(series=[
                    dict(name=_('Praise'), data=daily['praise']),
                    dict(name=_('Issues'), data=daily['issue']),
                    dict(name=_('Ideas'), data=daily['idea']),
                    ]
                ) if daily else None
            data['chart_data_json'] = json.dumps(chart_data)
    else:
        data.update({
            'opinion_count': 0,
            'opinions': None,
            'sent': get_sentiment(),
            'demo': {},
        })

    data['defaults'] = get_defaults(form)
    template = 'search/%ssearch.html' % (
        'mobile/' if request.mobile_site else '')
    return jingo.render(request, template, data)
