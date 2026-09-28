# django-oscar-blog

A blog app for [django-oscar](https://github.com/django-oscar/django-oscar):
posts, an Oscar dashboard section under **Content**, and posts that can
link out to catalogue products they mention.

## What this package does, and doesn't, do

- A `Post` model: title/slug/excerpt/body/featured image/author/status
  (draft/published)/publish date, plus `meta_title`/`meta_description` for
  SEO and a `related_products` many-to-many onto `catalogue.Product`.
- Storefront list/detail views (`oscar_blog.urls`) and a `PostSitemap`.
- An Oscar dashboard section (`oscar_blog.dashboard`) for staff to create,
  edit, and delete posts — list/create/update/delete views following the
  exact same conventions as Oscar's own `dashboard.pages` app (flatpages),
  including its permission model (`is_staff` by default).
- It does **not** ship a newsletter integration, a product-picker
  autocomplete widget (the dashboard form uses a plain multi-select — fine
  at a small catalogue's scale, worth swapping for something like Oscar's
  own Range product-search UI if it becomes unwieldy), or a "featured
  products" CTA anywhere in the storefront — see "Adding a CTA" below.

## Installation

```
uv add django-oscar-blog
```

Add to `INSTALLED_APPS`, **after** `catalogue`/`partner` (it references
`catalogue.Product`) and after `oscar.config.Shop`:

```python
INSTALLED_APPS = [
    ...,
    "oscar_blog.apps.OscarBlogConfig",
    "oscar_blog.dashboard.apps.BlogDashboardConfig",
]
```

Run `manage.py migrate` — this package ships its own migration.

## Wiring the storefront URLs

```python
# urls.py
urlpatterns = [
    path("blog/", include("oscar_blog.urls")),
    ...
]
```

Templates extend `oscar/layout.html` under `oscar_blog/post_list.html` and
`oscar_blog/post_detail.html` — override them the same way you'd override
any other Oscar template (a project-level `templates/oscar_blog/...`
directory).

## Wiring the dashboard in ("Content" menu)

Oscar's own `dashboard.apps.DashboardConfig.get_urls()` is a **hardcoded
list**, not auto-discovered — every dashboard section Oscar ships is added
there directly, and third-party sections have to fork that config the same
way you'd fork any other Oscar app. This package's own test suite
(`tests/dashboard.py`) is a working example of exactly this fork — copy its
shape into your project, e.g. a `dashboard/apps.py`:

```python
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
```

...and swap `"oscar.apps.dashboard.apps.DashboardConfig"` for your
project's own `"yourproject.dashboard.apps.DashboardConfig"` in
`INSTALLED_APPS`.

Then add the nav entry under **Content**, alongside Pages/Email
templates/Reviews, by overriding `OSCAR_DASHBOARD_NAVIGATION` (a plain
Django setting — copy Oscar's default from `oscar.defaults` and insert):

```python
{
    "label": _("Blog posts"),
    "url_name": "dashboard:blog-post-list",
},
```

into the `"Content"` entry's `"children"` list.

## Related products

`Post.related_products` is a plain (unordered) `ManyToManyField` onto
`catalogue.Product`. A published post's detail page lists them under
"Mentioned products", linking to each product's own page
(`post_detail.html`). Nothing on the `Product` side surfaces "posts that
mention me" yet — the reverse relation is available as
`product.blog_posts.all()` if a host project wants to add that to a
product page.

## Adding a CTA (deliberately not built here)

This package intentionally ships no newsletter-subscribe or
"promote this product" call-to-action anywhere in its templates — that's
host-project UI/UX scope (placement, copy, branding), not something a
reusable blog app should assume. If your project adds one, the natural
places are `oscar_blog/post_list.html`/`post_detail.html` (override them)
or a custom template tag included from there.

## Development

```
uv sync
uv run pytest
```

`tests/settings.py` boots a full (stock) Oscar app stack — this package
genuinely depends on Oscar's catalogue models, unlike a framework-agnostic
library, so its tests can't run against bare Django alone.
