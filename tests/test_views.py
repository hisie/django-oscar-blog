from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from oscar_blog.models import Post

pytestmark = pytest.mark.django_db


def make_post(**kwargs):
    defaults = {"title": "Hello world", "slug": "hello-world", "body": "Body."}
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


def test_list_view_only_shows_published_posts_to_anonymous(client):
    published = make_post(
        title="Published",
        slug="published",
        status=Post.Status.PUBLISHED,
        published_at=timezone.now() - timedelta(days=1),
    )
    make_post(title="Draft", slug="draft")

    response = client.get(reverse("blog:post-list"))

    assert response.status_code == 200
    titles = [post.title for post in response.context["posts"]]
    assert titles == [published.title]


def test_list_view_shows_drafts_to_staff(client, django_user_model):
    make_post(title="Draft", slug="draft")
    staff = django_user_model.objects.create_user(
        username="staff", email="staff@example.com", password="pw", is_staff=True
    )
    client.force_login(staff)

    response = client.get(reverse("blog:post-list"))

    titles = [post.title for post in response.context["posts"]]
    assert titles == ["Draft"]


def test_detail_view_404s_for_unpublished_post_to_anonymous(client):
    make_post()

    response = client.get(reverse("blog:post-detail", kwargs={"slug": "hello-world"}))

    assert response.status_code == 404


def test_detail_view_shows_related_products(client):
    from oscar.test.factories import create_product

    product = create_product(title="Palmera")
    post = make_post(status=Post.Status.PUBLISHED, published_at=timezone.now() - timedelta(days=1))
    post.related_products.add(product)

    response = client.get(post.get_absolute_url())

    assert response.status_code == 200
    assert list(response.context["related_products"]) == [product]
