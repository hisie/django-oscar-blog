import pytest
from django.urls import reverse

from oscar_blog.dashboard.forms import PostUpdateForm
from oscar_blog.models import Post

pytestmark = pytest.mark.django_db


def test_body_widget_has_no_html_required_attribute():
    # The real bug: TinyMCE hides this textarea, and a browser can't
    # focus a hidden "required" field to show its native validation
    # error — which silently blocks the whole form submit. Confirmed
    # live before this fix: "required" was present in the rendered HTML.
    form = PostUpdateForm()
    assert "required" not in str(form["body"])


def test_empty_body_is_still_rejected_server_side(client, django_user_model):
    staff = django_user_model.objects.create_superuser(
        username="staff", email="staff@example.com", password="pw"
    )
    client.force_login(staff)

    response = client.post(
        reverse("dashboard:blog-post-create"),
        {
            "title": "A post",
            "slug": "a-post",
            "excerpt": "",
            "body": "   ",
            "status": Post.Status.DRAFT,
            "meta_title": "",
            "meta_description": "",
            "related_products": [],
            "tags": "",
        },
    )

    assert response.status_code == 200
    assert "body" in response.context["form"].errors
    assert not Post.objects.exists()


def test_post_with_real_body_still_saves(client, django_user_model):
    staff = django_user_model.objects.create_superuser(
        username="staff", email="staff@example.com", password="pw"
    )
    client.force_login(staff)

    response = client.post(
        reverse("dashboard:blog-post-create"),
        {
            "title": "A post",
            "slug": "a-post",
            "excerpt": "",
            "body": "<p>Real content</p>",
            "status": Post.Status.DRAFT,
            "meta_title": "",
            "meta_description": "",
            "related_products": [],
            "tags": "",
        },
    )

    assert response.status_code == 302
    assert Post.objects.filter(slug="a-post").exists()
