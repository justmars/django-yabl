from typing import Optional

from django.http import HttpRequest
from django.template.response import TemplateResponse

from .models import TagItem
from .utils import LIST_BOOKMARKED, LIST_FILTERED, LIST_TAGS


def filtered_objs(
    request: HttpRequest, tag_slug: str, model_id: Optional[int] = None
) -> TemplateResponse:
    """Get objects tagged with `tag_slug`, optionally filtered by `model_id`, assuming user is authenticated."""
    context = {"user_tagged_objs": [], "tag_slug": tag_slug}
    if request.user.is_authenticated:
        context |= TagItem.set_context(request.user, tag_slug, model_id)
    return TemplateResponse(request, LIST_FILTERED, context)


def annotated_tags(request: HttpRequest) -> TemplateResponse:
    from .models import AbstractBookmarkable

    tags = []
    if request.user.is_authenticated:
        tags = TagItem.tagged.made_by_user(
            request.user, AbstractBookmarkable.__subclasses__()
        )
    return TemplateResponse(request, LIST_TAGS, {"tags": tags})


def bookmarked_objs(request: HttpRequest) -> TemplateResponse:
    objs = []
    if request.user.is_authenticated:
        objs = request.user.bookmark_set.all()
    context = {"bookmarked_objs": objs}
    return TemplateResponse(request, LIST_BOOKMARKED, context)
