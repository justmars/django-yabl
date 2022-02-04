from django.urls import path

from .views import BOOK, QUOTE, SampleBookDetail, homepage_view

app_name = "examples"
urlpatterns = (
    BOOK.make_patterns()
    + QUOTE.make_patterns()
    + [
        path(
            "book/detail/<int:pk>",
            SampleBookDetail.as_view(),
            name="book_detail",
        ),
        path("", homepage_view),
    ]
)
