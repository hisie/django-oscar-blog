from __future__ import annotations

from django.apps import apps
from django.urls import include, path

urlpatterns = [
    path("", include(apps.get_app_config("oscar").urls[0])),
    path("blog/", include("oscar_blog.urls")),
]
