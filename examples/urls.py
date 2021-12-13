from django.urls import path

from .views import BOOK, QUOTE, homepage_view

app_name = "examples"
urlpatterns = (
    BOOK.make_patterns() + QUOTE.make_patterns() + [path("", homepage_view)]
)
