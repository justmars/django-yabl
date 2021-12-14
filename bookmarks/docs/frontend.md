# Frontend Customization

1. The [base.html](./templates/base.html) uses the htmx/hyperscript example [modal.css](./examples/static/css/modal.css) and a bespoke [starter.css](./examples/static/css/starter.css) declared in an _app-level_ static folder.
2. The _app-level_ [modal.html](./bookmarks/templates/commons/modal.html) displays custom modals via htmx click.
3. The _app-level_ [panel.html](./tags/templates/tags/panel.html) provides content displayed within custom modals.
4. The modal is where backend actions – i.e. toggle bookmark status, add tags, remove tag – become operational.

## Overriding style

1. Modify `base.html` to use [insert _framework_ here].
2. Declare root-level `templates` directory, add a subdirectory `tags/` with a `panel.html`
3. Copy and paste the _app-level_ `panel.html` into the directory created in (2.)
4. Style the root-level `panel.html` based on inserted _framework_.

## Load custom modal

Load custom modal based on htmx custom modal [css style](https://htmx.org/examples/modal-custom/):

```jinja
<!-- adds a custom DOM element before the end of the body, adding a dark underlay to the DOM to highlight the modal's contents -->
<em hx-trigger="click"
    hx-get="{{url}}"
    hx-target="body"
    hx-swap="beforeend">
    view
</em>
```

## Post data on checkbox change

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

## Delete from backend and remove frontend element on click

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
