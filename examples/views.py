from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)
from django.views.generic import DetailView

from bookmarks.utils import Pathmaker
from bookmarks.views import (
    generic_add_tags,
    generic_del_tag,
    generic_get_item,
    generic_launch_modal,
    generic_toggle_status,
)

from .models import SampleBook, SampleQuote


def homepage_view(request: HttpRequest):
    context = {
        "book_list": SampleBook.objects.all(),
        "quote_list": SampleQuote.objects.all(),
        "user_list": get_user_model().objects.all(),
    }
    return TemplateResponse(request, "home.html", context)


class SampleBookDetail(LoginRequiredMixin, DetailView):
    model = SampleBook
    template_name = "book_detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotes_saved"] = self.get_object().quotes.filter(
            id__in=list(
                self.request.user.bookmark_set.filter(
                    content_type=ContentType.objects.get(
                        app_label="examples", model="samplequote"
                    )
                ).values_list("object_id", flat=True)
            )
        )
        return context


"""
? BOOKS
"""


@login_required
@require_GET
def launch_modal_samplebook(request: HttpRequest, pk: str) -> TemplateResponse:
    return generic_launch_modal(SampleBook, request, pk)


@require_GET
def get_item_samplebook(
    request: HttpRequest, pk: str, user_slug: Optional[str] = None
) -> TemplateResponse:
    return generic_get_item(SampleBook, request, pk, user_slug)


@login_required
@require_http_methods(["PUT"])
def toggle_status_samplebook(
    request: HttpRequest, pk: str
) -> TemplateResponse:
    return generic_toggle_status(SampleBook, request, pk)


@login_required
@require_POST
def add_tags_samplebook(request: HttpRequest, pk: str) -> TemplateResponse:
    return generic_add_tags(SampleBook, request, pk)


@login_required
@require_http_methods(["DELETE"])
def del_tag_samplebook(request: HttpRequest, pk: str) -> HttpResponse:
    return generic_del_tag(SampleBook, request, pk)


BOOK = Pathmaker(
    model_klass=SampleBook,
    launch_func=launch_modal_samplebook,
    get_item_func=get_item_samplebook,
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
    return generic_launch_modal(SampleQuote, request, pk)


@require_GET
def get_item_samplequote(
    request: HttpRequest, pk: str, user_slug: Optional[str] = None
) -> TemplateResponse:
    return generic_get_item(SampleQuote, request, pk, user_slug)


@login_required
@require_http_methods(["PUT"])
def toggle_status_samplequote(
    request: HttpRequest, pk: str
) -> TemplateResponse:
    return generic_toggle_status(SampleQuote, request, pk)


@login_required
@require_POST
def add_tags_samplequote(request: HttpRequest, pk: str) -> TemplateResponse:
    return generic_add_tags(SampleQuote, request, pk)


@login_required
@require_http_methods(["DELETE"])
def del_tag_samplequote(request: HttpRequest, pk: str) -> HttpResponse:
    return generic_del_tag(SampleQuote, request, pk)


QUOTE = Pathmaker(
    model_klass=SampleQuote,
    launch_func=launch_modal_samplequote,
    get_item_func=get_item_samplequote,
    toggle_status_func=toggle_status_samplequote,
    add_tags_func=add_tags_samplequote,
    del_tag_func=del_tag_samplequote,
)
