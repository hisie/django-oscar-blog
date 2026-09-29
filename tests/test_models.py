from datetime import timedelta

import pytest
from django.utils import timezone
from oscar.test.factories import create_product

from oscar_blog.models import Post

pytestmark = pytest.mark.django_db


def make_post(**kwargs):
    defaults = {
        "title": "Hello world",
        "slug": "hello-world",
        "body": "Some body text.",
    }
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


def test_draft_post_is_not_published():
    post = make_post()
    assert not post.is_published
    assert post not in Post.objects.published()


def test_published_post_with_past_date_is_published():
    post = make_post(status=Post.Status.PUBLISHED, published_at=timezone.now() - timedelta(days=1))
    assert post.is_published
    assert post in Post.objects.published()


def test_published_status_with_future_date_is_not_yet_visible():
    post = make_post(status=Post.Status.PUBLISHED, published_at=timezone.now() + timedelta(days=1))
    assert not post.is_published
    assert post not in Post.objects.published()


def test_effective_meta_falls_back_to_title_and_excerpt():
    post = make_post(excerpt="An excerpt.")
    assert post.effective_meta_title() == post.title
    assert post.effective_meta_description() == "An excerpt."

    post.meta_title = "Custom title"
    post.meta_description = "Custom description"
    assert post.effective_meta_title() == "Custom title"
    assert post.effective_meta_description() == "Custom description"


def test_related_products_accepts_catalogue_products():
    product = create_product()
    post = make_post()
    post.related_products.add(product)
    assert list(post.related_products.all()) == [product]
    assert list(product.blog_posts.all()) == [post]


def test_tags_can_be_added_and_are_shared_across_posts():
    post_a = make_post(title="A", slug="a")
    post_b = make_post(title="B", slug="b")

    post_a.tags.add("succulents", "care tips")
    post_b.tags.add("succulents")

    assert {t.name for t in post_a.tags.all()} == {"succulents", "care tips"}
    # Same tag name on two posts is the same Tag row, not a duplicate —
    # that's the whole point of a shared tag vocabulary (browsing by tag
    # across posts, not per-post free text).
    succulents_tag = post_a.tags.get(name="succulents")
    assert post_b.tags.get(name="succulents").pk == succulents_tag.pk
