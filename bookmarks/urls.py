from django.urls import path

from .views import annotated_tags, bookmarked_objs, filter_objects_by_tag_model

app_name = "bookmarks"
urlpatterns = [
    path(
        "tag/<slug:tag_slug>",
        filter_objects_by_tag_model,
        name="filter_objects_by_tag_models",
    ),
    path(
        "tag/<slug:tag_slug>/<int:model_id>",
        filter_objects_by_tag_model,
        name="filter_objects_by_tag_models",
    ),
    path("tags", annotated_tags, name="annotated_tags"),
    path("objs", bookmarked_objs, name="bookmarked_objs"),
]
