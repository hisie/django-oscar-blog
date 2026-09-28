from oscar.core.application import OscarConfig


class OscarBlogConfig(OscarConfig):
    name = "oscar_blog"
    label = "oscar_blog"
    verbose_name = "Blog"
    default_auto_field = "django.db.models.BigAutoField"
