from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from bookmarks.utils import MODAL_BASE, PANEL, Pathmaker

from .models import SampleBook, SampleQuote


def homepage_view(request: HttpRequest):
    context = {
        "book_list": SampleBook.objects.all(),
        "quote_list": SampleQuote.objects.all(),
    }
    return TemplateResponse(request, "home.html", context)


"""
? BOOKS
"""


@login_required
@require_GET
def launch_modal_samplebook(request: HttpRequest, pk: str) -> TemplateResponse:
    obj = get_object_or_404(SampleBook, pk=pk)
    panel = {"content_template": PANEL}
    context = obj.set_bookmarked_context(request.user) | panel
    return TemplateResponse(request, MODAL_BASE, context)


@login_required
@require_http_methods(["PUT"])
def toggle_status_samplebook(
    request: HttpRequest, pk: str
) -> TemplateResponse:
    obj = get_object_or_404(SampleBook, pk=pk)
    obj.toggle_bookmark(request.user)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


@login_required
@require_POST
def add_tags_samplebook(request: HttpRequest, pk: str) -> TemplateResponse:
    obj = get_object_or_404(SampleBook, pk=pk)
    if submitted := request.POST.get("tags"):
        if add_these := submitted.split(","):
            obj.add_tags(request.user, add_these)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


@login_required
@require_http_methods(["DELETE"])
def del_tag_samplebook(request: HttpRequest, pk: str) -> HttpResponse:
    obj = get_object_or_404(SampleBook, pk=pk)
    if delete_this := request.POST.get("tag"):
        obj.remove_tag(request.user, delete_this)
    return HttpResponse(headers={"HX-Trigger": "tagDeleted"})


BOOK = Pathmaker(
    model_klass=SampleBook,
    launch_func=launch_modal_samplebook,
    toggle_status_func=toggle_status_samplebook,
    add_tags_func=add_tags_samplebook,
    del_tag_func=del_tag_samplebook,
)

"""
? QUOTES
"""


@login_required
@require_GET
def launch_modal_samplequote(
    request: HttpRequest, pk: str
) -> TemplateResponse:
    obj = get_object_or_404(SampleQuote, pk=pk)
    panel = {"content_template": PANEL}
    context = obj.set_bookmarked_context(request.user) | panel
    return TemplateResponse(request, MODAL_BASE, context)


@login_required
@require_http_methods(["PUT"])
def toggle_status_samplequote(
    request: HttpRequest, pk: str
) -> TemplateResponse:
    obj = get_object_or_404(SampleQuote, pk=pk)
    obj.toggle_bookmark(request.user)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


@login_required
@require_POST
def add_tags_samplequote(request: HttpRequest, pk: str) -> TemplateResponse:
    obj = get_object_or_404(SampleQuote, pk=pk)
    if submitted := request.POST.get("tags"):
        if add_these := submitted.split(","):
            obj.add_tags(request.user, add_these)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


@login_required
@require_http_methods(["DELETE"])
def del_tag_samplequote(request: HttpRequest, pk: str) -> HttpResponse:
    obj = get_object_or_404(SampleQuote, pk=pk)
    if delete_this := request.POST.get("tag"):
        obj.remove_tag(request.user, delete_this)
    return HttpResponse(headers={"HX-Trigger": "tagDeleted"})


QUOTE = Pathmaker(
    model_klass=SampleQuote,
    launch_func=launch_modal_samplequote,
    toggle_status_func=toggle_status_samplequote,
    add_tags_func=add_tags_samplequote,
    del_tag_func=del_tag_samplequote,
)
