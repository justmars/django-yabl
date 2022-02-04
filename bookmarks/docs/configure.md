# Configuration

## Add to installed apps

INSTALLED_APPS = [
    "bookmarks", # new
]

## Add to urls.py

urlpatterns = [
    path("bookmarks/", include("bookmarks.urls")),
]

Let's assume an `examples` app containing a `SampleBook` model:

## Inherit from abstract base model

```python
# examples/models.py
from bookmarks.models import AbstractBookmarkable
class SampleBook(AbstractBookmarkable):
    ...
```

## Add verbose name to model

Add a `verbose_name` to `Meta.options` so that if referenced via its `Content_Type` _.name_, the assigned `verbose_name` appears.

```python
# examples/models.py
class SampleBook(AbstractBookmarkable):
    ...
    class Meta:
        verbose_name = "Book"  # see generic relations, e.g. content_type.name
        verbose_name_plural = "Books"
```

## Set display of instance content

Each display will be different because each model will have different fields / different html markup. Instead of rendering a separate template per model, can customize a model attribute via `format_html()`:

```python
# examples/models.py
from django.utils.html import format_html # new
from django.utils.safestring import SafeText # new

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

## Copy/paste view functions

Use template of preconfigured set of views, matching the same to another model, e.g. `ArbitraryPainting`.

```python
# examples/views.py
from django.template.response import TemplateResponse # new
from django.shortcuts import get_object_or_404 # new
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
) # new
from bookmarks.utils import Pathmaker, MODAL_BASE, PANEL # new

@login_required
@require_GET
def launch_modal_samplebook(request: HttpRequest, pk: str) -> TemplateResponse: # change view name
    obj = get_object_or_404(SampleBook, pk=pk) # change model to ArbitraryPainting
    panel = {"content_template": PANEL}
    context = obj.set_bookmarked_context(request.user) | panel
    return TemplateResponse(request, MODAL_BASE, context)


@login_required
@require_GET
def get_item_samplebook(request: HttpRequest, pk: str) -> TemplateResponse: # change view name
    obj = get_object_or_404(SampleBook, pk=pk) # change model to ArbitraryPainting
    context = obj.set_bookmarked_context(request.user)
    return TemplateResponse(request, PANEL, context)

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
    get_item_func=get_item_samplebook, # add changed view name
    toggle_status_func=toggle_status_samplebook, # add changed view name
    add_tags_func=add_tags_samplebook, # add changed view name
    del_tag_func=del_tag_samplebook, # add changed view name
)
```

The copy/pasting isn't the most elegant solution but it provides better understanding of the data flow.

## Set URLs

```python
# examples/urls.py
from .views import SAMPLEBOOK
from .apps import ExamplesConfig
app_name = ExamplesConfig.name # will match SampleBook.objects.get(pk=1)._meta.app_label
urlpatterns = SAMPLEBOOK.make_patterns() + [..., ] # add helper method to the original list
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

## Configure modal

One of the paths created in `make_patterns()` is the `launch_modal` path which can be customized by the model's `@modal` property.

```python
class SampleBook(AbstractBookmarkable)
    ...

    @property
    def modal(self) -> SafeText:
        """Return html with htmx modal launcher based on app_name. Presumes prior coordination with bookmarks.utils in urls.py"""
        raw = """<em hx-trigger="click"
                hx-get="{url}"
                hx-target="body"
                hx-swap="beforeend"
                hx-indicator="#{loader_id}"
                _="on mouseover add [@style=text-decoration:underline] to me
                    on mouseleave remove [@style=text-decoration:underline] from me
                "
                >view</em>
                <span id="{loader_id}" class="spinner-border htmx-indicator" role="status">
                    <span class="visually-hidden">Loading...</span>
                </span>
            """
        return format_html(
            raw,
            loader_id=f"spinner-{self.pk}",
            url=self.launch_modal_url,
        )
```

## Add modal element, ensure authenticated

If desired to place the `@modal` in a list view, consider the following example:

```jinja
<h2>{{header}}</h2>
<ul>
    {% for obj in obj_list %}
        <li>
            {{obj}}

            <!-- need to check if user is logged in before enabling a model property that, when clicked, will launch a modal -->

            {% if user.is_authenticated %}
                {{obj.modal}}
            {% endif %}
        </li>
    {% empty %}
        <h3> No {{header|lower}} supplied. </h3>
    {% endfor %}
</ul>
```

## Setup URL nav to all user subscriptions

```jinja
<nav>
    ...
    <a href="{% url 'bookmarks:bookmarked_objs' %}">Saved</a>
</nav>
```

## Setup URL nav to all user-made tags

```jinja
<nav>
    ...
     <a href="{% url 'bookmarks:annotated_tags' %}">Tags</a>
</nav> <!-- this will lead to the tags/tags.html which must be overriden -->
```

## Annotated tags customization

Look for `bookmark/tags/tagged_models.html` and copy its contents to `templates/tags/tagged_models.html` to override the models used:

```jinja
<!-- templates/tags/tagged_models.html -->
{% include './annotated_item.html' with count=tag.samplebook_count slug=tag.samplebook_slug idx=tag.samplebook_id %}
{% include './annotated_item.html' with count=tag.samplequote_count slug=tag.samplequote_slug idx=tag.samplequote_id %}
<!-- Do this for each model that you want to show a count of tags for -->
```

In the `examples` app, we declared two `AbstractBookmarkable` models: `SampleBook` and `SampleQuote`.

The `annotated_tags()` view gets implementing classes of `AbstractBookmarkable` annotates the tags queryset.

Still exploring best way to display this annotated list of tags in the template.

For now, override the `tags/tagged_models.html` template, replacing `samplebook` and `samplequote`, the _verbose model names_ of the implementing classes, with your selected models.

## Overrides styles

1. Modify `base.html` to use [insert _framework_ here].
2. Declare root-level `templates` directory, add the present subdirectories here:
   - `templates/bookmarks`
   - `templates/commons`
   - `templates/tags`
3. Copy and paste the _app-level_ `panel.html` into the directory created in (2.)
4. Style the root-level `panel.html` based on inserted _framework_.
