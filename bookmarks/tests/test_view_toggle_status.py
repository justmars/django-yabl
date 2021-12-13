from http import HTTPStatus

import pytest
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from bookmarks.utils import PANEL

ENDPOINT = lambda x: f"/samplebook/toggle_status/{x}"
ROUTE = lambda x: reverse(
    "examples:toggle_status_samplebook", kwargs={"pk": x}
)


@pytest.mark.django_db
def test_toggle_status_route_matches_instance_attribute(item):
    assert hasattr(item, "toggle_status_url")
    assert item.toggle_status_url == ROUTE(item.id)


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_toggle_status_anonymous_redirected_since_login_required(
    client, format_url, item
):
    response = client.get(format_url(item.id))
    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_toggle_status_from_unchecked_to_checkedauthenticated(
    client, format_url, item, potential_bookmarker
):
    # initialize, verify unbookmarked logged in user
    assert not item.is_bookmarked(potential_bookmarker)
    client.force_login(potential_bookmarker)
    url = format_url(item.id)

    # bookmark with logged in user
    response = client.put(url)
    assert item.is_bookmarked(potential_bookmarker)
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == PANEL


@pytest.mark.django_db
@pytest.mark.parametrize("format_url", [ENDPOINT, ROUTE])
def test_toggle_status_from_checked_to_unchecked_authenticated(
    client, format_url, item, first_bookmarker
):
    # initialize, verify previous bookmark
    assert item.is_bookmarked(first_bookmarker)
    client.force_login(first_bookmarker)
    url = format_url(item.id)

    # unbookmark with logged in user
    response = client.put(url)
    assert not item.is_bookmarked(first_bookmarker)
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == PANEL
