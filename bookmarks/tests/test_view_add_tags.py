from http import HTTPStatus

import pytest
from django.db.models import QuerySet
from django.template.response import TemplateResponse
from django.urls import reverse

from bookmarks.utils import PANEL

ENDPOINT = lambda x: f"/samplebook/add_tags/{x}"
ROUTE = lambda x: reverse("examples:add_tags_samplebook", kwargs={"pk": x})


@pytest.mark.django_db
def test_add_tags_route_matches_instance_attribute(item):
    assert hasattr(item, "add_tags_url")
    assert item.add_tags_url == ROUTE(item.id)


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_add_tags(client, item, format_url, potential_bookmarker):
    # initialize, no tags yet
    url = format_url(item.pk)
    client.force_login(potential_bookmarker)
    user_obj_tags = item.get_user_tags(potential_bookmarker)
    assert not user_obj_tags

    # tags to be added
    response = client.post(url, data={"tags": "alpha, beta, gamma"})
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == PANEL

    # check tags added
    tags = item.get_user_tags(potential_bookmarker)
    tag_names = tags.values_list("name", flat=True)
    assert isinstance(tags, QuerySet)
    assert set(tag_names) == set(["alpha", "beta", "gamma"])
