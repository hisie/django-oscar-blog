from django.urls import path
from django.utils.translation import gettext_lazy as _
from oscar.core.application import OscarDashboardConfig
from oscar.core.loading import get_class


class BlogDashboardConfig(OscarDashboardConfig):
    label = "blog_dashboard"
    name = "oscar_blog.dashboard"
    verbose_name = _("Blog dashboard")

    default_permissions = [
        "is_staff",
    ]

    def configure_permissions(self):
        DashboardPermission = get_class("dashboard.permissions", "DashboardPermission")

        self.permissions_map = {
            "blog-post-list": DashboardPermission.get("oscar_blog", "view_post"),
            "blog-post-create": DashboardPermission.get("oscar_blog", "view_post", "add_post"),
            "blog-post-update": DashboardPermission.get("oscar_blog", "view_post", "change_post"),
            "blog-post-delete": DashboardPermission.get("oscar_blog", "view_post", "delete_post"),
        }

    # pylint: disable=attribute-defined-outside-init
    def ready(self):
        self.list_view = get_class("oscar_blog.dashboard.views", "PostListView")
        self.create_view = get_class("oscar_blog.dashboard.views", "PostCreateView")
        self.update_view = get_class("oscar_blog.dashboard.views", "PostUpdateView")
        self.delete_view = get_class("oscar_blog.dashboard.views", "PostDeleteView")
        self.configure_permissions()

    def get_urls(self):
        urls = [
            path("", self.list_view.as_view(), name="blog-post-list"),
            path("create/", self.create_view.as_view(), name="blog-post-create"),
            path("update/<int:pk>/", self.update_view.as_view(), name="blog-post-update"),
            path("delete/<int:pk>/", self.delete_view.as_view(), name="blog-post-delete"),
        ]
        return self.post_process_urls(urls)
