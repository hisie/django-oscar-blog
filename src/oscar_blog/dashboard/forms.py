from django import forms
from django.utils.translation import gettext_lazy as _
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


class PostUpdateForm(forms.ModelForm):
    related_products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label=_("Related products"),
        help_text=_(
            "Products this post mentions — shown on the post page and available to the newsletter."
        ),
        widget=forms.SelectMultiple(attrs={"size": 10}),
    )

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
