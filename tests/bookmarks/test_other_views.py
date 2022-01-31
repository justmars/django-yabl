from http import HTTPStatus

import pytest
from django.template.response import TemplateResponse
from django.urls import reverse

from bookmarks.utils import LIST_BOOKMARKED, LIST_FILTERED, LIST_TAGS


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    [
        "/",
        "/bookmarks/objs",
        reverse("bookmarks:bookmarked_objs"),
        "/bookmarks/tags",
        reverse("bookmarks:annotated_tags"),
    ],
)
def test_view_endpoint(client, endpoint):
    response = client.get(endpoint)
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_view_bookmarked_list(client, first_bookmarker):
    url = reverse("bookmarks:bookmarked_objs")
    client.force_login(first_bookmarker)
    response = client.get(url)
    assert "bookmarked_objs" in response.context_data
    assert response.template_name == LIST_BOOKMARKED
    assert len(response.context_data["bookmarked_objs"]) == 1


@pytest.mark.django_db
def test_view_annotated_tags(client, potential_bookmarker, item_with_tags):
    url = reverse("bookmarks:annotated_tags")
    client.force_login(potential_bookmarker)
    response = client.get(url)
    assert "tags" in response.context_data
    assert response.template_name == LIST_TAGS
    assert len(response.context_data["tags"]) == 2


@pytest.mark.django_db
def test_view_filtered_list(
    client, potential_bookmarker, item_with_tags, model_id
):
    kwargs = {"tag_slug": "omega", "model_id": model_id}
    url = reverse("bookmarks:filtered_objs", kwargs=kwargs)
    client.force_login(potential_bookmarker)
    response = client.get(url)
    assert "user_tagged_objs" in response.context_data
    assert response.template_name == LIST_FILTERED
    assert len(response.context_data["user_tagged_objs"]) == 1
