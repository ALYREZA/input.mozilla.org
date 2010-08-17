import urllib

from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode

import jinja2
from jingo import register

from .forms import DEFAULTS


@register.function
@jinja2.contextfunction
def sites_url(context, form, fragment_id=None, **kwargs):
    """Return the current form values as URL parameters.

    Values are taken from the given form and can be overriden using kwargs.
    This is used to modify parts of a query without losing search context.
    The 'page' is always reset if not explicitly given.
    Parameters are only included if the values differ from the default.
    """
    parameters = form.cleaned_data.copy()
    # page is reset on every change of search
    for name in form.cleaned_data.keys():
        if name == 'page' or parameters[name] == DEFAULTS[name]:
            del parameters[name]
    for name, value in kwargs.iteritems():
        if not value == DEFAULTS[name]:
            parameters[name] = value

    # If this is a single-site page, convert the site ID to search criteria.
    if form.cleaned_data['site'] and context['site']:
        del parameters['site']
        if 'q' not in kwargs and 'page' not in kwargs:
            parameters['q'] = context['site'].url

    parts = [reverse("website_issues")]
    if len(parameters):
        parts.extend(["?", urllib.urlencode(parameters)])
    if fragment_id is not None:
        parts.extend(["#", fragment_id])
    return ''.join(parts)


@register.filter
def without_protocol(url):
    if url.find("://") == -1: return url
    return url[ url.find("://")+3 : ]


@register.filter
def protocol(url):
    return url[ : url.find("://")+3 ]


@register.filter
def as_unicode(str_or_unicode):
    return smart_unicode(str_or_unicode)
