from django.views.generic import DetailView, ListView

from oscar_blog.models import Post


class VisiblePostMixin:
    """Staff see every post (draft or published, same "see everything
    regardless of activation" convention catalogue's browsable_dashboard()
    uses for staff); anonymous/customer visitors only see published ones —
    an unpublished slug 404s for them rather than 403ing, simplest correct
    behaviour for a page that shouldn't reveal it exists at all."""

    def get_queryset(self):
        qs = Post.objects.all()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return qs
        return qs.published()


class PostListView(VisiblePostMixin, ListView):
    model = Post
    template_name = "oscar_blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 12


class PostDetailView(VisiblePostMixin, DetailView):
    model = Post
    template_name = "oscar_blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_products"] = self.object.related_products.all()
        return context
