from django.urls import path

from bookmarks.utils import Pathmaker

from .models import SampleBook, SampleQuote
from .views import SampleBookDetail, homepage_view

app_name = "examples"
urlpatterns = (
    Pathmaker(SampleBook).make_patterns()
    + Pathmaker(SampleQuote).make_patterns()
    + [
        path(
            "book/detail/<int:pk>",
            SampleBookDetail.as_view(),
            name="book_detail",
        ),
        path("", homepage_view),
    ]
)
