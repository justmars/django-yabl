from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Q, Value
from django.db.models.expressions import Expression
from django.db.models.query import QuerySet


class UserAnnotations(models.Manager):
    def filter_by_user(self, user) -> QuerySet:
        """Get all tags in which the `user` has bookmarked to a bookmarked model instance."""
        qs = (
            super()
            .get_queryset()
            .prefetch_related("bookmarked__bookmarker")
            .prefetch_related("bookmarked__content_type")
            .filter(bookmarked__bookmarker=user)
            .distinct()
        )
        return qs

    def prep_for_annotation(self, user, model: models.Model):
        """Generate values for `_count`, `_id`, and `_slug` prefixed with the model `label`, e.g if the model is `Decision`, the annotation keys are `decision_count`, `decision_id`, and `decision_slug`. The `_id` refers to the `contenttype` id, the `slug` refers to the lowercased name of the model."""
        label = model._meta.model_name.lower()
        type_of_model = ContentType.objects.get_for_model(model)
        by_type = Q(bookmarked__content_type=type_of_model)
        by_user = Q(bookmarked__bookmarker=user)
        return {
            f"{label}_count": Count("bookmarked", filter=by_type & by_user),
            f"{label}_id": Value(type_of_model.id),
            f"{label}_slug": Value(model._meta.verbose_name),
        }

    def made_by_user(self, user, models: list[models.Model]) -> QuerySet:
        """Tags filtered by user then each tag is annotated with different contenttypes."""
        qs = self.filter_by_user(user)
        for model in models:
            values = self.prep_for_annotation(user, model)
            qs = qs.annotate(**values)
        return qs


class MarkedTags(models.Manager):
    def _bookmarker_by_user(self, user):
        """Each user may have bookmarked to objects which have an , this fetches all bookmarks made by a specific user."""
        return (
            super()
            .get_queryset()
            .select_related("bookmarker")
            .prefetch_related("tags")
            .filter(bookmarker=user)
            .distinct()
        )

    def extract_from(
        self, user, tag, content_id: Optional[int] = None
    ) -> QuerySet:
        """bookmarks tagged by the `user` with a `tag_slug`. The resulting queryset can be of different models since the `bookmark` model is generic; but if `cat_id` is set, the instances must be of the same contenttype model represented by the `cat_id`."""
        qs = self._bookmarker_by_user(user).filter(tags=tag)
        if content_id:
            qs = qs.filter(
                content_type=ContentType.objects.get_for_id(content_id)
            )
        return qs
