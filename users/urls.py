from django.urls import path

from .views import get_saved_books, get_saved_quotes, get_user_profile

app_name = "users"
urlpatterns = [
    path("quotes/<str:username>", get_saved_quotes, name="get_saved_quotes"),
    path("books/<str:username>", get_saved_books, name="get_saved_books"),
    path("user/<str:username>", get_user_profile, name="get_user_profile"),
]
