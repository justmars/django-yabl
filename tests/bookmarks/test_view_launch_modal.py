from http import HTTPStatus

import pytest
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from bookmarks.utils import MODAL_BASE

ENDPOINT = lambda x: f"/samplebook/launch_modal/{x}"
ROUTE = lambda x: reverse("examples:launch_modal_samplebook", kwargs={"pk": x})


@pytest.mark.django_db
def test_launch_modal_route_matches_instance_attribute(item):
    assert hasattr(item, "launch_modal_url")
    assert item.launch_modal_url == ROUTE(item.id)


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_launch_modal_anonymous_redirected_since_login_required(
    client, format_url, item
):
    response = client.get(format_url(item.id))
    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_launch_modal_authenticated(
    client, format_url, item, potential_bookmarker
):
    client.force_login(potential_bookmarker)
    response = client.get(format_url(item.id))
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == MODAL_BASE
