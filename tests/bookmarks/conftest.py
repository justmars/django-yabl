import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from bookmarks.models import TagItem
from examples.models import SampleBook


@pytest.fixture
def author():
    return get_user_model().objects.create_user(
        username="juan", password="bar"
    )


@pytest.fixture
def item(author) -> SampleBook:
    return SampleBook.objects.create(title="sample", author=author)


@pytest.fixture
def model_id(author) -> int:
    x = ContentType.objects.get_for_model(SampleBook)
    return x.id


@pytest.fixture
def potential_bookmarker():
    return get_user_model().objects.create_user(
        username="maria", password="bar"
    )


@pytest.fixture
def first_bookmarker(potential_bookmarker, item: SampleBook):
    item.toggle_bookmark(potential_bookmarker)
    return potential_bookmarker


@pytest.fixture
def a_tag(author):
    return TagItem.objects.create(title="sample", author=author)


@pytest.fixture
def tag_name_to_delete():
    return "omega"


@pytest.fixture
def item_with_tags(potential_bookmarker, tag_name_to_delete, item: SampleBook):
    item.add_tags(potential_bookmarker, [tag_name_to_delete, "delta"])
    return item
