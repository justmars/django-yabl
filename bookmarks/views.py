from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from .models import TagItem
from .utils import LIST_BOOKMARKED, LIST_FILTERED, LIST_TAGS, MODAL_BASE, PANEL


def generic_launch_modal(
    model_klass: ContentType, request: HttpRequest, pk: str
) -> TemplateResponse:
    """Launches the modal containing tagging and bookmarking functions"""
    obj = get_object_or_404(model_klass, pk=pk)
    panel = {"content_template": PANEL}
    context = obj.set_bookmarked_context(request.user) | panel
    return TemplateResponse(request, MODAL_BASE, context)


def generic_get_item(
    model_klass: ContentType,
    request: HttpRequest,
    pk: str,
    user_slug: Optional[str] = None,
) -> TemplateResponse:
    """Launches the object containing tagging and bookmarking functions"""
    obj = get_object_or_404(model_klass, pk=pk)
    context = {}
    if user_slug:
        if user_found := get_object_or_404(
            get_user_model(), username=user_slug
        ):
            context = obj.set_bookmarked_context(user_found)
    else:
        if request.user.is_authenticated:
            context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


def generic_toggle_status(
    model_klass: ContentType, request: HttpRequest, pk: str
) -> TemplateResponse:
    """Toggles the requesting user's preference re: bookmarked status of the object"""
    obj = get_object_or_404(model_klass, pk=pk)
    obj.toggle_bookmark(request.user)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


def generic_add_tags(
    model_klass: ContentType, request: HttpRequest, pk: str
) -> TemplateResponse:
    """Auto-bookmarks and tags the object with the submitted POST input form"""
    obj = get_object_or_404(model_klass, pk=pk)
    if submitted := request.POST.get("tags"):
        if add_these := submitted.split(","):
            obj.add_tags(request.user, add_these)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


def generic_del_tag(
    model_klass: ContentType, request: HttpRequest, pk: str
) -> HttpResponse:
    """Deletes a previously added user-made tag of a specific object"""
    obj = get_object_or_404(model_klass, pk=pk)
    if delete_this := request.POST.get("tag"):
        obj.remove_tag(request.user, delete_this)
    return HttpResponse(headers={"HX-Trigger": "tagDeleted"})


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
