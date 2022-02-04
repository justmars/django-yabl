from django import template
from django.db.models import QuerySet

register = template.Library()


@register.inclusion_tag("bookmarks/items_to_load.html", takes_context=True)
def populate_bookmark_items(context, qs: QuerySet):
    return {"items_to_load": qs, "user_profile": context["user_profile"]}
