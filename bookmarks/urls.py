from django.urls import path

from .views import annotated_tags, bookmarked_objs, filtered_objs

app_name = "bookmarks"
urlpatterns = [
    path(
        "tag/<slug:tag_slug>/<int:model_id>",
        filtered_objs,
        name="filtered_objs",
    ),
    path("tag/<slug:tag_slug>", filtered_objs, name="filtered_objs"),
    path("tags", annotated_tags, name="annotated_tags"),
    path("objs", bookmarked_objs, name="bookmarked_objs"),
]
