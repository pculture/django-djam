from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseForbidden
from django.template.defaultfilters import slugify

from djam.views.base import DefaultRedirectView


class Riff(object):
    widgets = []
    riff_classes = []
    verbose_name = None
    slug = None
    namespace = None
    app_name = None
    default_redirect_view = DefaultRedirectView

    def __init__(self, parent=None, namespace=None, app_name=None):
        self.parent = parent
        if self.verbose_name is None:
            raise ImproperlyConfigured('Please give me a verbose name')
        if self.slug is None:
            self.slug = slugify(self.verbose_name)
        self.namespace = namespace or self.namespace or self.slug
        if parent is None:
            self.base_riff = self
            self.full_namespace = self.namespace
        else:
            self.base_riff = parent.base_riff
            self.full_namespace = ":".join((parent.full_namespace, self.namespace))
        self.riffs = list()
        for riff_cls in self.riff_classes:
            self.register_riff(riff_cls)

    def register_riff(self, riff_class):
        self.riffs.append(riff_class(parent=self))

    def get_default_url(self):
        """
        Returns the default base url for this riff. Must be implemented by
        subclasses.

        """
        raise NotImplementedError('Subclasses must implement get_default_url.')

    def get_urls(self):
        urlpatterns = self.get_extra_urls()

        urlpatterns += patterns('',
            url(r'^$', self.default_redirect_view.as_view(riff=self)),
        )

        for riff in self.riffs:
            urlpatterns += patterns('',
                url(r'^{slug}/'.format(slug=riff.slug),
                    include(riff.get_urls_tuple())),
            )

        return urlpatterns

    def get_extra_urls(self):
        return patterns('',)

    def get_urls_tuple(self):
        return self.get_urls(), self.app_name, self.namespace

    def get_view_kwargs(self):
        return {'riff': self}

    def has_permission(self, request):
        if self.parent:
            return self.parent.has_permission(request)
        return True

    def is_hidden(self, request):
        return not self.has_permission(request)

    def get_unauthorized_response(self, request):
        if self.base_riff is not self:
            return self.base_riff.get_unauthorized_response(request)
        return HttpResponseForbidden()

    def wrap_view(self, view):
        return view

    def reverse(self, name, *args, **kwargs):
        return reverse('{namespace}:{viewname}'.format(namespace=self.full_namespace, viewname=name),
                       args=args, kwargs=kwargs)
