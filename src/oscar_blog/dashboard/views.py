from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from oscar.core.loading import get_classes

from oscar_blog.models import Post

PostSearchForm, PostUpdateForm = get_classes(
    "oscar_blog.dashboard.forms", ("PostSearchForm", "PostUpdateForm")
)


class PostListView(generic.ListView):
    template_name = "oscar/dashboard/blog/index.html"
    model = Post
    form_class = PostSearchForm
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    desc_template = "%(main_filter)s%(title_filter)s%(status_filter)s"

    def get_queryset(self):
        # pylint: disable=attribute-defined-outside-init
        self.desc_ctx = {
            "main_filter": _("All posts"),
            "title_filter": "",
            "status_filter": "",
        }
        queryset = self.model.objects.all().order_by("-date_created")

        # pylint: disable=attribute-defined-outside-init
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data["title"]:
            queryset = queryset.filter(title__icontains=data["title"])
            self.desc_ctx["title_filter"] = _(" with title containing '%s'") % data["title"]

        if data["status"]:
            queryset = queryset.filter(status=data["status"])
            self.desc_ctx["status_filter"] = _(" with status '%s'") % data["status"]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        context["queryset_description"] = self.desc_template % self.desc_ctx
        return context


class PostCreateUpdateMixin:
    template_name = "oscar/dashboard/blog/update.html"
    model = Post
    form_class = PostUpdateForm
    context_object_name = "post"

    def get_success_url(self):
        messages.success(self.request, _("Post '%s' saved") % self.object.title)
        return reverse("dashboard:blog-post-list")


class PostCreateView(PostCreateUpdateMixin, generic.CreateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = _("Create new post")
        return ctx

    def form_valid(self, form):
        post = form.save(commit=False)
        if post.author_id is None and self.request.user.is_authenticated:
            post.author = self.request.user
        post.save()
        form.save_m2m()
        self.object = post
        return HttpResponseRedirect(self.get_success_url())


class PostUpdateView(PostCreateUpdateMixin, generic.UpdateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.object.title
        return ctx


class PostDeleteView(generic.DeleteView):
    template_name = "oscar/dashboard/blog/delete.html"
    model = Post

    def get_success_url(self):
        messages.success(self.request, _("Deleted post '%s'") % self.object.title)
        return reverse("dashboard:blog-post-list")
