from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext as _

from wagtail.wagtailadmin.forms import SearchForm
from wagtail.wagtailsearch.backends import get_search_backend
from wagtail.wagtailsearch.index import class_is_indexed


class SearchableListMixin(object):
    search_box_placeholder = _("Search")
    search_fields = None

    def get_search_form(self):
        return SearchForm(self.request.GET if self.request.GET.get('q') else None, placeholder=self.search_box_placeholder)

    def get_queryset(self):
        queryset = super(SearchableListMixin, self).get_queryset()
        search_form = self.get_search_form()

        if search_form.is_valid():
            q = search_form.cleaned_data['q']

            if class_is_indexed(queryset.model):
                search_backend = get_search_backend()
                queryset = search_backend.search(q, queryset, fields=self.search_fields)
            else:
                filters = {
                    field + '__icontains': q
                    for field in self.search_fields or []
                }

                queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        if 'search_form' not in kwargs:
            kwargs['search_form'] = self.get_search_form()
            kwargs['is_searching'] = bool(self.request.GET.get('q'))

        return super(SearchableListMixin, self).get_context_data(**kwargs)
