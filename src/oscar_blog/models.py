from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PostQuerySet(models.QuerySet):
    def published(self):
        """Posts visible to an anonymous storefront visitor: status is
        published *and* the publish date has actually arrived — a post
        can be marked published ahead of time and stay hidden until then,
        same "activated but not yet live" shape as catalogue.Product's
        web_activated field."""
        return self.filter(
            status=Post.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        )


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    excerpt = models.TextField(
        _("excerpt"),
        blank=True,
        help_text=_("Short summary shown in listings and used as a default meta description."),
    )
    body = models.TextField(_("body"))
    featured_image = models.ImageField(
        _("featured image"), upload_to="blog/posts/%Y/%m/%d", blank=True
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        related_name="blog_posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(
        _("published at"),
        null=True,
        blank=True,
        help_text=_(
            "A post only appears on the storefront once this date has passed "
            "and status is Published."
        ),
    )

    meta_title = models.CharField(_("meta title"), max_length=255, blank=True)
    meta_description = models.CharField(_("meta description"), max_length=255, blank=True)

    # Products the post mentions, so a post can link out to them and a
    # product can (later) show which posts raise information about it —
    # deliberately a plain M2M, not ordered: a post's own body/links carry
    # any narrative ordering, this is just "which products are related".
    related_products = models.ManyToManyField(
        "catalogue.Product",
        verbose_name=_("related products"),
        related_name="blog_posts",
        blank=True,
    )

    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("date updated"), auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ("-published_at", "-date_created")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post-detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return (
            self.status == self.Status.PUBLISHED
            and self.published_at is not None
            and self.published_at <= timezone.now()
        )

    def effective_meta_title(self):
        return self.meta_title or self.title

    def effective_meta_description(self):
        return self.meta_description or self.excerpt
