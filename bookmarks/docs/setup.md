# Setup

## Install in virtual environment

```zsh
.venv> pip3 install django-allauth # for authentication purposes only
.venv> pip3 install django-bookmark-and-tag # poetry add django-bookmark-and-tag
```

## Add to project settings

[Setup](bookmarks/docs/allauth.md) django allauth first for simple authentication urls / views / templates/.

```python
# settings.py
INSTALLED_APPS = [
    ...
    # for authentication purposes only
    "django.contrib.sites", # need by allauth

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # add the following:
    "bookmarks", # new
    "examples" # your app that will be bookmarked / tagged
    ...
]
```

## Add bookmarks urls

```python
# urls.py
urlpatterns = [
    ...
    path("accounts/", include("allauth.urls")), # for ensuring authentication only
    path("bookmarks/", include("bookmarks.urls")), # new
    path("", include("examples.urls")), # 'examples.urls' is just for purposes of testing this ought to be replaced by the app whose model will be bookmarked / tagged
]
```

## Check base.html

- [ ] `htmx`/`hyperscript`
- [ ] `modal.css` for loading modals
- [ ] `<nav>` contains `allauth` tags

## Run migration

```zsh
.venv> python manage.py migrate
```

## Run tests

```zsh
.venv> pytest --ds=config.settings --cov
```

## Optional fixtures

Sample fixtures can be loaded into the `SampleBook` and `SampleQuote` model found in examples/models.py:

```zsh
>>> python manage.py loaddata bookquotes.yaml # fixtures which show sample books
```
