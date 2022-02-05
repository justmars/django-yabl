from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.views.generic import DetailView

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
    template_name = "examples/book_detail.html"
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
