from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse


def get_user_profile(request: HttpRequest, username: str):
    context: dict = {}
    context["user_profile"] = get_object_or_404(get_user_model(), username=username)
    return TemplateResponse(request, "users/user_profile.html", context)


def get_saved_books(request: HttpRequest, username: str):
    context: dict = {}
    context["user_profile"] = get_object_or_404(get_user_model(), username=username)
    return TemplateResponse(request, "users/saved_books.html", context)


def get_saved_quotes(request: HttpRequest, username: str):
    context: dict = {}
    context["user_profile"] = get_object_or_404(get_user_model(), username=username)
    return TemplateResponse(request, "users/saved_quotes.html", context)
