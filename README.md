# django-yabl

Yet another bookmarking library (yabl) for Django. Bookmark and tag arbitrary models.

`AbstractBookmarkable` contains `bookmarks` field. This enables arbitrary child models, e.g. Movies, Books, Laws, Clothes, etc., to inherit uniform properties for bookmarking and tagging.

The `bookmarks` field is mapped to a generic `Bookmark` model containing:

1. the authenticated user adding the bookmark, i.e. the `bookmarker`;
2. the concrete model instance referenced, i.e. the _bookmarked_;[^1] and
3. a ManyToMany `tags` field which maps to a `TagItem` model.

[^1]: The model is referenced via a `content_type` and an `object_id`

## AbstractBookmarkable

The abstraction makes each inheriting instance _bookmarkable_ and _taggable_ by authenticated users.

| Attributes                        | Purpose                                                    |
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
| @`get_item_url`               | URL to load the panel containde within custom modal                                 |
| @`add_tags_url`                   | URL to POST tags added                                     |
| @`del_tag_url`                    | URL to DELETE tag added                                    |
| @`toggle_status_url`              | URL to toggle bookmark status of an object instance added  |
| @`object_content_for_panel`       | Content when custom modal is loaded; **must** be overriden |

## Modal-based UX

### What is the concept?

The modal is where the user interacts – i.e. toggle bookmark status, add tags, remove tag (see table above) – with the data.

### How is the modal styled?

See the htmx/hyperscript example [modal.css](bookmarks/static/css/modal.css).

### How is the modal constructed during run-time?

See _app-level_ [modal.html](bookmarks/templates/commons/modal.html) which shows a modal via htmx click on the `@launch_modal_url` property.

### What are the pre-made contents of the modal?

The _app-level_ [panel.html](bookmarks/templates/tags/templates/tags/panel.html), contained within the modal, shows an actionable form for saving the bookmarable object and associating said object with tags:

1. The submission of tags is POST'ed through the `add_tags_url`.
2. The deletion of tags is DELETE'ed through the `del_tag_url`.
3. The bookmark toggle is PUT'ed through the `toggle_status_url`.

## Setup

1. Download and [install](bookmarks/docs/setup.md).
2. See [configuration](bookmarks/docs/configure.md) of models to be bookmarked and tagged.
3. Examine [frontend](bookmarks/docs/frontend.md) setup using `htmx/hyperscript`.
