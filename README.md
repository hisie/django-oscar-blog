# django-oscar-blog

A blog app for [django-oscar](https://github.com/django-oscar/django-oscar):
posts, an Oscar dashboard section under **Content**, and posts that can
link out to catalogue products they mention.

## What this package does, and doesn't, do

- A `Post` model: title/slug/excerpt/body/featured image/author/status
  (draft/published)/publish date, plus `meta_title`/`meta_description` for
  SEO, a `related_products` many-to-many onto `catalogue.Product`, and
  tags (via [django-taggit](https://github.com/jazzband/django-taggit)).
- Storefront list/detail views (`oscar_blog.urls`) and a `PostSitemap`.
- An Oscar dashboard section (`oscar_blog.dashboard`) for staff to create,
  edit, and delete posts — list/create/update/delete views following the
  exact same conventions as Oscar's own `dashboard.pages` app (flatpages),
  including its permission model (`is_staff` by default).
- It does **not** ship a newsletter integration or a "featured products"
  CTA anywhere in the storefront — see "Adding a CTA" below. The
  related-products picker defaults to a plain multi-select but has an
  opt-in AJAX autocomplete mode — see "Related products" below.

## Installation

```
uv add django-oscar-blog
```

Add to `INSTALLED_APPS`, **after** `catalogue`/`partner` (it references
`catalogue.Product`) and after `oscar.config.Shop`:

```python
INSTALLED_APPS = [
    ...,
    "taggit",
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

**Dashboard picker widget — two modes, one setting:**

```python
OSCAR_BLOG_PRODUCT_AUTOCOMPLETE = True  # default: False
```

- **Off (default)**: a plain `<select multiple>` with every product
  rendered as an `<option>`. Fine at a small catalogue's scale; at real
  scale every dashboard post-edit page load pulls in the whole catalogue.
- **On**: the dashboard's related-products field switches to Oscar's own
  `oscar.apps.dashboard.catalogue.widgets.ProductSelectMultiple` — a
  Select2 widget backed by Oscar's already-installed
  `dashboard:catalogue-product-lookup` endpoint
  (`oscar.apps.dashboard.catalogue.views.ProductLookupView`, a real
  `title__icontains` search, already staff-permission-gated). Only the
  *currently selected* products are pre-rendered; everything else loads
  as the user types. No new backend endpoint needed — this project's
  `dashboard/forms.py` just wires Oscar's existing one in, plus one real
  fix Oscar itself doesn't apply consistently: `ProductSelectMultiple`
  needs an explicit `class="select2 product-select"` to actually get
  AJAX-backed search (confirmed against
  `oscar/static/oscar/js/oscar/dashboard.js`'s `initSelects()` — without
  it, the field would still render, just silently degraded to searching
  only the few options already in the page).

**Requires** `oscar.apps.dashboard.catalogue` installed (it almost
certainly already is — it's the products dashboard). If it isn't, turning
this setting on will fail with a `NoReverseMatch` on
`dashboard:catalogue-product-lookup`, not silently.

## Tags

Uses [django-taggit](https://github.com/jazzband/django-taggit) directly
(BSD-licensed) rather than a hand-rolled tag model — `Post.tags` is a
`TaggableManager`, editable in the dashboard as a plain comma-separated
field (taggit's own default widget, no extra code needed). Tags are
shared across posts (the same tag name is the same `Tag` row everywhere,
not per-post free text), and the storefront list view supports
`?tag=<slug>` filtering — both `oscar_blog/post_list.html` and
`post_detail.html` render each post's tags as links to that filtered
list. Run `manage.py migrate` after adding `taggit` to `INSTALLED_APPS` —
it ships its own migrations for the shared `Tag`/`TaggedItem` tables.

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
