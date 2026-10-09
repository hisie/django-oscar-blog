import pytest
from django.test import override_settings
from django.urls import reverse
from oscar.test.factories import create_product

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


def test_staff_can_set_tags_via_the_dashboard_form(staff_client):
    response = staff_client.post(
        reverse("dashboard:blog-post-create"),
        {
            "title": "A tagged post",
            "slug": "a-tagged-post",
            "excerpt": "",
            "body": "Body text.",
            "status": Post.Status.DRAFT,
            "meta_title": "",
            "meta_description": "",
            "related_products": [],
            "tags": "succulents, care tips",
        },
    )

    assert response.status_code == 302
    post = Post.objects.get(slug="a-tagged-post")
    assert {t.name for t in post.tags.all()} == {"succulents", "care tips"}


def test_staff_can_delete_post(staff_client):
    post = Post.objects.create(title="A post", slug="a-post", body="Body.")

    response = staff_client.post(reverse("dashboard:blog-post-delete", kwargs={"pk": post.pk}))

    assert response.status_code == 302
    assert not Post.objects.filter(pk=post.pk).exists()


def test_related_products_widget_defaults_to_plain_multiselect(staff_client):
    create_product(title="Palmera")
    post = Post.objects.create(title="A post", slug="a-post", body="Body.")

    response = staff_client.get(reverse("dashboard:blog-post-update", kwargs={"pk": post.pk}))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'name="related_products"' in content
    # The plain widget renders every product as an <option> up front, and
    # isn't the AJAX widget — select2.min.js is always loaded dashboard-
    # wide (base layout), so what actually distinguishes "plain" is the
    # absence of the AJAX lookup wiring, not "select2" as a bare string.
    assert "Palmera" in content
    assert "data-ajax-url" not in content


@override_settings(OSCAR_BLOG_PRODUCT_AUTOCOMPLETE=True)
def test_related_products_widget_switches_to_ajax_autocomplete_when_enabled(staff_client):
    selected = create_product(title="Palmera")
    create_product(title="Ficus")  # not selected — must NOT be pre-rendered
    post = Post.objects.create(title="A post", slug="a-post", body="Body.")
    post.related_products.add(selected)

    response = staff_client.get(reverse("dashboard:blog-post-update", kwargs={"pk": post.pk}))

    assert response.status_code == 200
    content = response.content.decode()
    # Oscar's own form-field rendering appends " form-control" to whatever
    # class the widget sets, so this checks the widget's own classes are
    # present, not an exact class="..." string.
    assert "select2 product-select" in content
    assert 'data-ajax-url="/dashboard/catalogue/product-lookup/"' in content
    # The real point of the AJAX widget: only the already-selected product
    # is pre-rendered, not the whole catalogue — this is what regressed
    # without the field.widget.choices reassignment (dashboard/forms.py).
    assert "Palmera" in content
    assert "Ficus" not in content


@override_settings(OSCAR_BLOG_PRODUCT_AUTOCOMPLETE=True)
def test_ajax_autocomplete_lookup_endpoint_is_reachable(staff_client):
    create_product(title="Palmera")

    response = staff_client.get(reverse("dashboard:catalogue-product-lookup"), {"q": "Palm"})

    assert response.status_code == 200
    assert response.json()["results"][0]["text"] == "Palmera"


def test_excerpt_is_a_plain_textarea_without_the_rich_text_editor(staff_client):
    response = staff_client.get(reverse("dashboard:blog-post-create"))

    form = response.context["form"]
    assert "no-widget-init" in form["excerpt"].field.widget.attrs["class"]
    # The body keeps the editor.
    assert "no-widget-init" not in form["body"].field.widget.attrs.get("class", "")
