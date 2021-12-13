from http import HTTPStatus

import pytest
from django.http.response import HttpResponse
from django.urls import reverse

ENDPOINT = lambda x: f"/samplebook/del_tag/{x}"
ROUTE = lambda x: reverse("examples:del_tag_samplebook", kwargs={"pk": x})


@pytest.mark.django_db
def test_del_tag_route_matches_instance_attribute(item):
    assert hasattr(item, "del_tag_url")
    assert item.del_tag_url == ROUTE(item.id)


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_del_tag(
    client,
    item_with_tags,
    format_url,
    potential_bookmarker,
    tag_name_to_delete,
):
    url = format_url(item_with_tags.pk)
    client.force_login(potential_bookmarker)
    assert item_with_tags.get_user_tags(potential_bookmarker).count() == 2

    response = client.delete(f"{url}?tag={tag_name_to_delete}")
    assert isinstance(response, HttpResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.headers["HX-Trigger"] == "tagDeleted"
