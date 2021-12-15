# Frontend Customization

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
