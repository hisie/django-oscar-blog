from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from oscar.apps.dashboard.catalogue.widgets import ProductSelectMultiple
from oscar.core.loading import get_model

from oscar_blog.models import Post

Product = get_model("catalogue", "Product")


class PostSearchForm(forms.Form):
    title = forms.CharField(required=False, label=_("Title"))
    status = forms.ChoiceField(
        required=False,
        label=_("Status"),
        choices=[("", "---------"), *Post.Status.choices],
    )


def _related_products_widget() -> forms.Widget:
    """Plain <select multiple> by default — every product gets rendered
    into the page, fine for a handful of products, painful at real
    catalogue scale. OSCAR_BLOG_PRODUCT_AUTOCOMPLETE=True (opt-in, see
    README) switches to Oscar's own ProductSelectMultiple instead, backed
    by Oscar's already-installed, already staff-permission-gated
    dashboard:catalogue-product-lookup endpoint (oscar.apps.dashboard.
    catalogue.views.ProductLookupView) — no new lookup view needed, this
    project just wires Oscar's own into place.

    ProductSelectMultiple's optgroups() (oscar.forms.widgets.RemoteSelect)
    only ever renders the *currently selected* options — everything else
    loads via AJAX as the user types — which is what actually avoids the
    "every product in one page load" problem; a plain <select> with
    select2 layered on top for cosmetics would still render every option
    into the HTML.

    The explicit "select2 product-select" class is necessary, not
    decorative: confirmed against oscar/static/oscar/js/oscar/dashboard.js
    — its initSelects() only wires up AJAX-backed select2 (reading
    data-ajax-url) for elements matching 'select.select2'; without that
    class the field would still render (via the *other*, always-on select2
    init pass) but only search the handful of options already in the page,
    silently defeating the whole point. ProductSelectMultiple itself never
    sets this class (only its single-select sibling, ProductSelect, does,
    in its own __init__) — confirmed by reading oscar/forms/widgets.py.
    """
    if getattr(settings, "OSCAR_BLOG_PRODUCT_AUTOCOMPLETE", False):
        return ProductSelectMultiple(attrs={"class": "select2 product-select"})
    return forms.SelectMultiple(attrs={"size": 10})


class PostUpdateForm(forms.ModelForm):
    related_products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label=_("Related products"),
        help_text=_(
            "Products this post mentions — shown on the post page and available to the newsletter."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Not a class-level widget= on the field above: that would be
        # evaluated once at import time, before a test (or a host project
        # reloading settings) could change OSCAR_BLOG_PRODUCT_AUTOCOMPLETE.
        # Resolving it fresh per instantiation keeps the toggle live.
        field = self.fields["related_products"]
        field.widget = _related_products_widget()
        # ModelChoiceField.choices is a property whose setter pushes onto
        # self.widget.choices — already run once, against the *old* widget,
        # by super().__init__() above. Swapping .widget afterwards doesn't
        # re-trigger it, so the new widget's .choices defaults to Select's
        # own __init__ value ([], a plain list) instead of the
        # ModelChoiceIterator RemoteSelect.optgroups() checks for
        # (oscar/forms/widgets.py) — without this line, ProductSelectMultiple
        # would silently render zero options, not even the selected ones.
        # Confirmed live via PostDashboardAutocompleteTests, not assumed.
        field.widget.choices = field.choices

    class Meta:
        model = Post
        fields = (
            "title",
            "slug",
            "excerpt",
            "body",
            "featured_image",
            "status",
            "published_at",
            "meta_title",
            "meta_description",
            "related_products",
        )
        widgets = {
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
