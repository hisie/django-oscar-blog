import pytest
from django.urls import reverse

from oscar_blog.models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_client(client, django_user_model):
    # A superuser, not just is_staff=True: the dashboard's per-view
    # permissions_map (configure_permissions() in dashboard/apps.py) checks
    # real model permissions (oscar_blog.view_post etc.), which only a
    # superuser has by default without explicitly granting them — same
    # persona Oscar's own dashboard test suite uses for a full-access user.
    staff = django_user_model.objects.create_superuser(
        username="staff", email="staff@example.com", password="pw"
    )
    client.force_login(staff)
    return client


def test_anonymous_is_redirected_to_login(client):
    response = client.get(reverse("dashboard:blog-post-list"))
    assert response.status_code == 302


def test_staff_can_list_posts(staff_client):
    Post.objects.create(title="A post", slug="a-post", body="Body.")

    response = staff_client.get(reverse("dashboard:blog-post-list"))

    assert response.status_code == 200
    assert response.context["post_list"].count() == 1


def test_staff_can_create_post_and_is_set_as_author(staff_client, django_user_model):
    response = staff_client.post(
        reverse("dashboard:blog-post-create"),
        {
            "title": "A new post",
            "slug": "a-new-post",
            "excerpt": "",
            "body": "Body text.",
            "status": Post.Status.DRAFT,
            "meta_title": "",
            "meta_description": "",
            "related_products": [],
        },
    )

    assert response.status_code == 302
    post = Post.objects.get(slug="a-new-post")
    assert post.author.username == "staff"


def test_staff_can_delete_post(staff_client):
    post = Post.objects.create(title="A post", slug="a-post", body="Body.")

    response = staff_client.post(reverse("dashboard:blog-post-delete", kwargs={"pk": post.pk}))

    assert response.status_code == 302
    assert not Post.objects.filter(pk=post.pk).exists()
