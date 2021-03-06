from __future__ import unicode_literals

from django.conf.urls import patterns, url

from djam.riffs.base import Riff
from djam.views.auth import LoginView, LogoutView


class AuthRiff(Riff):
    login_view = LoginView
    logout_view = LogoutView
    verbose_name = 'Auth'

    def get_login_kwargs(self):
        return self.get_view_kwargs()

    def get_logout_kwargs(self):
        return self.get_view_kwargs()
    
    def get_urls(self):
        urlpatterns = super(AuthRiff, self).get_urls()

        urlpatterns += patterns('',
            url(r'^logout/$',
                self.wrap_view(self.logout_view.as_view(**self.get_logout_kwargs())),
                name='logout'),
            url(r'^login/$',
                self.wrap_view(self.login_view.as_view(**self.get_login_kwargs())),
                name='login'),
        )

        return urlpatterns
    
    def has_permission(self, request):
        # Login/logout don't care whether you're authenticated.
        return True

    def get_default_url(self):
        if self.parent is not None:
            return self.parent.get_default_url()
        return self.reverse('login')
