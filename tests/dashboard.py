"""Test-only fork of Oscar's DashboardConfig that adds the blog_dashboard
section under /dashboard/blog/. This is exactly the fork a host project
needs to make to wire django-oscar-blog's dashboard in for real — see
README.md's "Wiring into a host project" section, which points here.
"""

from __future__ import annotations

from django.apps import apps
from django.urls import include, path
from oscar.apps.dashboard.apps import DashboardConfig as OscarDashboardConfig


class DashboardConfig(OscarDashboardConfig):
    def ready(self):
        super().ready()
        self.blog_app = apps.get_app_config("blog_dashboard")

    def get_urls(self):
        urls = super().get_urls()
        urls.append(path("blog/", include(self.blog_app.urls[0])))
        return urls
