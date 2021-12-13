# django-yabl

Yet another bookmarking library (yabl) for Django. Bookmark and tag arbitrary models.

## Overview

The `AbstractBookmarkable` contains a `bookmarks` field mapped to a generic `Bookmark` model containing:

1. the authenticated user adding the bookmark, i.e. the `bookmarker`;
2. the concrete model instance referenced, i.e. the _bookmarked_;[^1] and
3. a ManyToMany `tags` field which maps to a `TagItem` model.

[^1]: The model is referenced via a `content_type` and an `object_id`

This abstraction makes each instance _bookmarkable_ and _taggable_ by users.

Specifically the following attributes are enabled:

| Attribute                         | Purpose                                                    |
| --------------------------------- | ---------------------------------------------------------- |
| `is_bookmarked`(user)             | Check whether object instance is bookmarked or not         |
| `get_bookmarked`(user)            | Get instances of model that user has bookmarked            |
| `get_user_tags`(user)             | If user bookmarked, get user-made tags on instance         |
| `toggle_bookmark`(user)           | Toggle bookmark status as bookmarked or not                |
| `add_tags`(user, tags: list[str]) | Add unique tags, accepts a list of names                   |
| `remove_tag`(user, tag: str)      | Delete an existing tag name from tags previously added     |
| `set_bookmarked_context`(user)    | Combines relevant urls and attributes for template output  |
| @`modal`                          | Custom modal enables: _toggle_, _add tags_, _remove tag_   |
| @`launch_modal_url`               | URL to launch custom modal                                 |
| @`add_tags_url`                   | URL to POST tags added                                     |
| @`del_tag_url`                    | URL to DELETE tag added                                    |
| @`toggle_status_url`              | URL to toggle bookmark status of an object instance added  |
| @`object_content_for_panel`       | Content when custom modal is loaded; **must** be overriden |

## Pre-requisites

1. `django-allauth` setup
2. `htmx` basics
3. Overriding Django templates

## Initial setup

### Install in virtual environment

```zsh
.venv> pip3 install django-allauth # for authentication purposes only
.venv> pip3 install django-bookmark-and-tag # poetry add django-bookmark-and-tag
```

### Add to project settings

```python
# settings.py
INSTALLED_APPS = [
    ...
    # for authentication purposes only
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # add the following:
    "bookmarks", # new
    "examples" # your app that will be bookmarked / tagged
    ...
]
```

### Setup django-allauth

A basic configuration just to enable easy access to authentication urls / views / templates:

```python
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

Add `templates` root directory:

```python
TEMPLATES = [
    {
        ...
        "DIRS": [BASE_DIR / "templates"],  # added
        ...
    }
```

Create a file under this specific directory to override allauth defaults:

```jinja
<!-- templates/account/base.html -->
{% extends 'base.html' %}
{% block title %} Authentication | BrandX {% endblock title %}

<!-- This overrides allauth /templates base.html -->

{% block content %}
{% endblock content %}
```

### Add bookmarks urls

```python
# urls.py
urlpatterns = [
    ...
    path("accounts/", include("allauth.urls")), # for ensuring authentication only
    path("bookmarks/", include("bookmarks.urls")), # new
    path("", include("examples.urls")), # 'examples.urls' is just for purposes of testing this ought to be replaced by the app whose model will be bookmarked / tagged
]
```

### Run migration

```zsh
.venv> python manage.py migrate
```

### Run tests

```zsh
.venv> pytest --ds=config.settings --cov
```

### Optional fixtures

Sample fixtures can be loaded into the `SampleBook` and `SampleQuote` model found in examples/models.py:

```zsh
>>> python manage.py loaddata bookquotes.yaml # fixtures which show sample books
```

## Backend Configuration

Let's assume an `examples` app containing a `SampleBook` model:

### Configure models.py

#### Add mixin to target model

Add an `AbstractBookmarkable` mixin to the models.py:

```python
# examples/models.py
class SampleBook(AbstractBookmarkable):
    ...
```

#### Add verbose name for contenttypes

Add a `verbose_name` to `Meta.options` so that if referenced via its `Content_Type` _.name_, the assigned `verbose_name` appears.

```python
# examples/models.py
class SampleBook(AbstractBookmarkable):
    ...
    class Meta:
        verbose_name = "Book"  # see generic relations, e.g. content_type.name
        verbose_name_plural = "Books"
```

#### Add mixin for attributes

Each book instance `obj` has access to `@`properties and methods requiring a `user`:

#### Customize display of model in panel

Must declare an @`object_content_for_panel` in the inheriting model.

Each display will be different because each model will have different fields / different html markup. Instead of rendering a separate template per model, can customize a model attribute via `format_html()`:

```python
# examples/models.py
class SampleBook(AbstractBookmarkable):
    ...
    @property
    def object_content_for_panel(self) -> SafeText: # customizes appearance of a specific book within the custom modal
        return format_html(
            """
            <h2>{title}</h2>
            <h3>{author}</h3>
            <p>{excerpt}</p>
            """,
            title=self.title,
            excerpt=self.excerpt,
            author=f"{self.author.first_name} {self.author.last_name}",
        )
```

### Configure views.py (copy/paste)

Copy and paste a preconfigured set of views, matching the same to another model, e.g. `ArbitraryPainting`. See sample set of views using a `SampleBook` model:

```python
# examples/views.py
from bookmarks.utils import Pathmaker, MODAL_BASE, PANEL

@login_required
@require_GET
def launch_modal_samplebook(request: HttpRequest, pk: str) -> TemplateResponse: # change view name
    obj = get_object_or_404(SampleBook, pk=pk) # change model to ArbitraryPainting
    panel = {"content_template": PANEL}
    context = obj.set_bookmarked_context(request.user) | panel
    return TemplateResponse(request, MODAL_BASE, context)


@login_required
@require_http_methods(["PUT"])
def toggle_status_samplebook(
    request: HttpRequest, pk: str
) -> TemplateResponse: # change view name
    obj = get_object_or_404(SampleBook, pk=pk) # change model to ArbitraryPainting
    obj.toggle_bookmark(request.user)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


@login_required
@require_POST
def add_tags_samplebook(request: HttpRequest, pk: str) -> TemplateResponse: # change view name
    obj = get_object_or_404(SampleBook, pk=pk) # change model to ArbitraryPainting
    if submitted := request.POST.get("tags"):
        if add_these := submitted.split(","):
            obj.add_tags(request.user, add_these)
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)


@login_required
@require_http_methods(["DELETE"])
def del_tag_samplebook(request: HttpRequest, pk: str) -> HttpResponse: # change view name
    obj = get_object_or_404(SampleBook, pk=pk) # change model to ArbitraryPainting
    if delete_this := request.POST.get("tag"):
        obj.remove_tag(request.user, delete_this)
    return HttpResponse(headers={"HX-Trigger": "tagDeleted"})

"""
Each view function from app/`views.py` related to a particular model should be imported into app/`urls.py`. The views can be consolidated to a single pattern based on a `Pathmaker` helper dataclass defined in bookmark/utils.py.
"""
BOOK = Pathmaker(
    model_klass=SampleBook, # change model to ArbitraryPainting
    launch_func=launch_modal_samplebook, # add changed view name
    toggle_status_func=toggle_status_samplebook, # add changed view name
    add_tags_func=add_tags_samplebook, # add changed view name
    del_tag_func=del_tag_samplebook, # add changed view name
)
```

The copy/pasting isn't the most elegant solution but it provides better understanding of the data flow.

### Configure urls.py

Declare a urls.py's `app_name`. The value declared _must match_ the model object's `._meta.app_label`.

So in the `SampleBook` model example above, since model is contained in the `examples` app, can configure the urls.py likeso:

```python
# examples/urls.py
from .views import SAMPLEBOOK
app_name = "examples" #  = SampleBook.objects.get(pk=1)._meta.app_label
urlpatterns = (SAMPLEBOOK.make_patterns())
```

The reason for the matching requirement is that `django.urls.reverse()` functions will rely on this convention to call urls from the object instance with a pre-determined property value, e.g.:

```zsh
>>> book_obj = SampleBook.objects.first()
>>> book_obj.launch_modal_url
'/samplebook/launch_modal/1'
>>> quote_obj = SampleQuote.objects.first()
>>> quote_obj.launch_modal_url
'/samplequote/launch_modal/5500a731-7682-4157-9f26-19412e44c560'
```

### Override tags/tags.html

In the `examples` app, we declared two `AbstractBookmarkable` models: `SampleBook` and `SampleQuote`.

The view `annotated_tags()` effectively determines implemeting classes of `AbstractBookmarkable` and produces the proper annotations.

Still exploring best way to display this annotated list of tags in the template.

For now, can override the `tags/tags.html` template, replacing `samplebook` and `samplequote`, the _verbose model names_ of the implementing classes, with your selected models.

```jinja
{% for tag in tags %}
    ...<!-- Do this for each model that you want to show a count of tags for -->
    {% include './item.html' with count=tag.samplebook_count slug=tag.samplebook_slug idx=tag.samplebook_id %}
    {% include './item.html' with count=tag.samplequote_count slug=tag.samplequote_slug idx=tag.samplequote_id %}
    ...
{% endfor %}
```

## Frontend Customization

### Basic design

1. The [base.html](./templates/base.html) uses the htmx/hyperscript example [modal.css](./examples/static/css/modal.css) and a bespoke [starter.css](./examples/static/css/starter.css) declared in an _app-level_ static folder.
2. The _app-level_ [modal.html](./bookmarks/templates/commons/modal.html) displays custom modals via htmx click.
3. The _app-level_ [panel.html](./tags/templates/tags/panel.html) provides content displayed within custom modals.
4. The modal is where backend actions – i.e. toggle bookmark status, add tags, remove tag – become operational.

### Overriding style

1. Modify `base.html` to use [insert _framework_ here].
2. Declare root-level `templates` directory, add a subdirectory `tags/` with a `panel.html`
3. Copy and paste the _app-level_ `panel.html` into the directory created in (2.)
4. Style the root-level `panel.html` based on inserted _framework_.

### UX via htmx & hyperscript

1. Load custom modal based on htmx custom modal [css style](https://htmx.org/examples/modal-custom/):

   ```jinja
   <!-- adds a custom DOM element before the end of the body, adding a dark underlay to the DOM to highlight the modal's contents -->
   <em hx-trigger="click"
       hx-get="{{url}}"
       hx-target="body"
       hx-swap="beforeend">
       view
   </em>
   ```

2. Post data on checkbox change:

   ```jinja
   <!-- 'closest section' assumes a parent container <section> -->
   <section>
       <input
           hx-trigger="change"
           hx-put="{{url}}"
           hx-target="closest section"
           type="checkbox"
           {% if is_bookmarked %}
               checked
           {% endif %}
       >
           Bookmark
       </input>
   </section>
   ```

3. Delete from backend and remove frontend element on click

   ```jinja
   <!-- badge <span>x</span> for easy deletion; when clicked, a DELETE request is sent to the backend. Once deleted, the frontend receives a trigger "tagDeleted" to remove the DOM element targeted by deletion. -->
   <small id="del_this">
       Thing to delete
       <span
           hx-trigger="click"
           hx-confirm="Are you sure you want to delete this?"
           hx-delete="{{url}}"
           hx-swap="none"
           _="on tagDeleted transition opacity to 0 then remove #del_this"
       >x</span>
   </small>
   ```
