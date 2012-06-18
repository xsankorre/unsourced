import re
import HTMLParser
from urlparse import urlparse
import lxml.html
from tornado.options import define, options

htmlparser = HTMLParser.HTMLParser()

def from_html(html):
    txt = html
    # html entities
    txt = htmlparser.unescape(txt)
    # comments
    txt = re.compile(r'<!--.*-->',re.DOTALL).sub('',txt)
    # tags
    txt = re.compile(r'<[^<]*?>',re.DOTALL).sub('',txt)
    # compress spaces
    txt = re.compile(r'\s{2,}',re.DOTALL).sub(' ',txt)
    return txt





def highlight(html,strings,cls):
    for s in strings:
        pat = re.compile(re.escape(s), re.IGNORECASE)
        html = pat.sub('<span class="%s">%s</span>' % (cls,s), html)
    return html


def domain(url):
    """ return domain of url, stripped of www. prefix """
    o = urlparse(url)
    domain = o.hostname
    domain = re.sub('^www[.]', '', domain)
    return domain



# adaptor by James Crasta on WTForms mailing list
class TornadoMultiDict(object):
    def __init__(self, handler):
        self.handler = handler

    def __iter__(self):
        return iter(self.handler.request.arguments)

    def __len__(self):
        return len(self.handler.request.arguments)

    def __contains__(self, name):
        # We use request.arguments because get_arguments always returns a
        # value regardless of the existence of the key.
        return (name in self.handler.request.arguments)

    def getlist(self, name):
        # get_arguments by default strips whitespace from the input data,
        # so we pass strip=False to stop that in case we need to validate
        # on whitespace.
        return self.handler.get_arguments(name, strip=False)



def parse_config_file(path):
    """Rewrite tornado default parse_config_file.
    
    Parses and loads the Python config file at the given path.
    
    This version allow customize new options which are not defined before
    from a configuration file.
    """
    config = {}
    execfile(path, config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])




class Paginator:
    """ paginator object for wrapping an sqlalchemy query """

    def __init__(self, query, per_page, current_page, page_url_fn):
        self.query = query
        self.per_page = per_page
        self.cur = current_page
        self._total_items = None
        self.page_url = page_url_fn

    @property
    def items(self):
        return self.query.\
            offset((self.cur-1)*self.per_page).\
            limit(self.per_page).\
            all()

    @property
    def total_items(self):
        if self._total_items is None:
            self._total_items = self.query.count()
        return self._total_items


    @property
    def total_pages(self):
        return (max(0,self.total_items-1) // self.per_page)+1;

    def __iter__(self):
        """ helper for rendering: step over the page numbers, returning None where should be a gap """
        MID_PAD=3
        END_PAD=2

        mid=(max(1,self.cur-MID_PAD), min(self.cur+MID_PAD, self.total_pages)+1)
        left=(1, min(END_PAD+1, mid[0]))
        right=(max((self.total_pages+1)-END_PAD, mid[1]), self.total_pages+1)

        for p in range(left[0],left[1]):
            yield p
        if mid[0]>left[1]:
            yield None  # a gap
        for p in range(mid[0],mid[1]):
            yield p
        if right[0]>mid[1]:
            yield None  # a gap
        for p in range(right[0],right[1]):
            yield p


    @property
    def previous(self):
        """ return previous page number (or None)"""
        if self.cur>1:
            return self.cur-1
        else:
            return None

    @property
    def next(self):
        """ return next page number (or None)"""
        if self.cur<self.total_pages:
            return self.cur+1
        else:
            return None


def fix_url(url):
    """ prepend "http://" to protocoless urls """
    if url is None:
        return url
    o = urlparse(url)
    if not o[0]:
        url = 'http://' + url
    return url



