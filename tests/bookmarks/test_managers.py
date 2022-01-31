import pytest
from django.db.models.query import QuerySet

from bookmarks.models import Bookmark, TagItem


@pytest.mark.django_db
def test_bookmarked_qs_no_model_id(potential_bookmarker, item_with_tags):
    tag = TagItem.objects.get(name="omega")
    qs = Bookmark.objects_tagged.extract_from(potential_bookmarker, tag)
    assert isinstance(qs, QuerySet)
    assert qs.count() == 1


@pytest.mark.django_db
def test_bookmarked_qs_with_model_id(
    potential_bookmarker, item_with_tags, model_id
):
    tag = TagItem.objects.get(name="omega")
    qs = Bookmark.objects_tagged.extract_from(
        potential_bookmarker, tag, model_id
    )
    assert isinstance(qs, QuerySet)
    assert qs.count() == 1


@pytest.mark.django_db
def test_filtered_objs(potential_bookmarker, item_with_tags):
    context = TagItem.set_context(potential_bookmarker, "omega")
    assert isinstance(context, dict)
    assert "user_tagged_objs" in context
    assert isinstance(context["user_tagged_objs"], QuerySet)
    assert context["user_tagged_objs"].count() == 1


@pytest.mark.django_db
def test_filtered_objs_filtered_by_model_id(
    potential_bookmarker, item_with_tags, model_id
):
    context = TagItem.set_context(potential_bookmarker, "omega", model_id)
    assert isinstance(context, dict)
    assert "user_tagged_objs" in context
    assert isinstance(context["user_tagged_objs"], QuerySet)
    assert context["user_tagged_objs"].count() == 1
