# Setup django-allauth

## Install

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    ...
]
```

## Configure

```python
# config/settings.py
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
SITE_ID = 1
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_LOGOUT_ON_GET = True  # no need to confirm logout
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "/"
```

## Add URL

```python
# urls.py
urlpatterns = [
    ...
    path("accounts/", include("allauth.urls")), # for ensuring authentication only
    ...
]
```

## Enable Root Template

Add `templates` root directory:

```python
TEMPLATES = [
    {
        ...
        "DIRS": [BASE_DIR / "templates"],  # added
        ...
    }
```

## Override Templates

Create a file under `templates/account/base.html` to override allauth defaults:

```jinja
<!-- templates/account/base.html -->
{% extends 'base.html' %}
{% block title %} Authentication | BrandX {% endblock title %}

<!-- This overrides allauth /templates base.html -->

{% block content %}
{% endblock content %}
```
