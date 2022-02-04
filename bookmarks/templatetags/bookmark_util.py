from django import template
from django.db.models import QuerySet

register = template.Library()


@register.inclusion_tag("bookmarks/items_to_load.html")
def populate_bookmark_items(qs: QuerySet):
    return {"items_to_load": qs}
