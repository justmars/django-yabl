import pytest


@pytest.mark.django_db
def test_sample_has_bookmarks(item):
    assert hasattr(item, "bookmarks")


@pytest.mark.django_db
def test_toggled_bookmark(item, potential_bookmarker):
    assert not item.is_bookmarked(potential_bookmarker)
    assert item.toggle_bookmark(potential_bookmarker)
    assert item.is_bookmarked(potential_bookmarker)
