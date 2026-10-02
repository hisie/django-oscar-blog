# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- `Post.body`'s dashboard widget no longer renders an HTML `required`
  attribute. TinyMCE replaces the textarea with a hidden input plus a
  separate visible iframe, syncing content back only on submit — the
  browser's native "required field" validation runs *before* that sync,
  can't focus a `display:none` field to show its error, and silently
  blocked the entire save (confirmed live: "An invalid form control...
  is not focusable" in the console, no request ever sent). Non-blank
  `body` is still enforced server-side, in `clean_body()`.

## [0.3.0] - 2026-09-29

### Added

- Tags (via [django-taggit](https://github.com/jazzband/django-taggit)):
  `Post.tags`, editable in the dashboard, `?tag=<slug>` filtering on the
  storefront list, tag links on both list and detail pages.

## [0.2.0] - 2026-09-28

### Added

- `OSCAR_BLOG_PRODUCT_AUTOCOMPLETE` setting: switches the dashboard's
  related-products field from a plain `<select multiple>` (every product
  rendered up front) to Oscar's own AJAX/Select2 `ProductSelectMultiple`,
  backed by Oscar's already-installed `dashboard:catalogue-product-lookup`
  endpoint — no new backend needed.

### Fixed

- `ProductSelectMultiple` needs an explicit `class="select2 product-select"`
  to actually get AJAX-backed search (confirmed against
  `dashboard.js`'s `initSelects()`) — without it the field silently
  degrades to searching only the options already on the page.
- Swapping a `ModelMultipleChoiceField`'s widget after `super().__init__()`
  drops its `ModelChoiceIterator` (a Django property-setter timing issue)
  — the AJAX widget would have rendered zero options, not even the
  currently-selected ones, without reassigning `field.widget.choices`
  after the swap.

## [0.1.0] - 2026-09-28

### Added

- Initial `Post` model: title/slug/excerpt/body/featured image/author/
  status (draft/published)/publish date, `meta_title`/`meta_description`
  for SEO, `related_products` M2M onto `catalogue.Product`.
- Storefront list/detail views and a sitemap.
- An Oscar dashboard section under Content, built on the same pattern as
  Oscar's own `dashboard.pages` (flatpages) app — list/create/update/
  delete, `is_staff`-gated by default.
- 13 tests, 89% coverage.

[Unreleased]: https://github.com/hisie/django-oscar-blog/compare/0.3.0...HEAD
[0.3.0]: https://github.com/hisie/django-oscar-blog/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/hisie/django-oscar-blog/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/hisie/django-oscar-blog/releases/tag/0.1.0
