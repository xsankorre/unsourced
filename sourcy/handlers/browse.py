from datetime import datetime,timedelta

import tornado.auth
from sqlalchemy import Date,not_
from sqlalchemy.sql.expression import cast,func
from sqlalchemy.orm import subqueryload
from wtforms import Form, SelectField, RadioField, HiddenField, BooleanField, TextField, PasswordField, FileField, validators

from base import BaseHandler
from sourcy.models import Article,Action,Lookup,Tag,TagKind,UserAccount,Comment,article_tags
from sourcy.util import Paginator
from sourcy.util import TornadoMultiDict
from sourcy.uimodules import searchresults

date_defs = [
    {'id': 'today', 'label': "Today", 'delta': timedelta(days=1)},
    {'id': '1week', 'label': "Past week", 'delta': timedelta(days=7)},
    {'id': '30days', 'label': "Past 30 days", 'delta': timedelta(days=30)},
    {'id': '1year', 'label':"Past year", 'delta': timedelta(days=365)},
    ]

class FiltersForm(Form):
    DATE_CHOICES = [('all','All')] + [(v['id'],v['label']) for v in date_defs]
    date = RadioField("Narrow by Date", choices=DATE_CHOICES, default="all")

#$('form').bind('submit', function(e){
#    e.preventDefault();
#    //do your stuff
#});

class BrowseHandler(BaseHandler):
    def get(self):
        page = int(self.get_argument('p',1))

        filters = FiltersForm(TornadoMultiDict(self))

        arts = self.session.query(Article).\
            options(subqueryload(Article.tags,Article.sources,Article.comments))

        if filters.validate():
            date_def = next((d for d in date_defs if d['id']==filters.date.data), None)
            if date_def:
                day_from = datetime.utcnow().date() - date_def['delta']
                arts = arts.filter(cast(Article.pubdate, Date) >= day_from)

#        tags = self.session.query(Tag).filter(Tag.name.in_(tag_filts))
#        if tag_filts:
#            arts = arts.filter(Article.tags.any(Tag.name.in_(tag_filts)))

            day_to = None

            if day_to:
                arts = arts.filter(cast(Article.pubdate, Date) <= day_to)

        arts = arts.order_by(Article.pubdate.desc())

        pager = Paginator(arts, 100, page)
        if self.is_xhr():
            results = searchresults(self)
            self.finish(results.render(pager=pager))
        else:
            self.render("browse.html",filters=filters,pager=pager)


handlers = [
    (r'/browse', BrowseHandler),
    ]

