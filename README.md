# django-yabl

Yet another bookmarking library (yabl) for Django. Bookmark and tag arbitrary models.

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

## Setup

1. Download and [install](bookmarks/docs/setup.md).
2. See [configuration](bookmarks/docs/configure.md) of models to be bookmarked and tagged.
3. Consider [frontend](bookmarks/docs/fronend.md) setup using `htmx/hyperscript`.
