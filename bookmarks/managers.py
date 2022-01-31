from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Q, Value
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
        """Using the prefix of the model `label`, generate values for `_count`, `_id`, and `_slug`.

        e.g if the model is `SampleBook`, the generated keys are `samplebook_count`, `samplebook_id`, and `samplebook_slug`.

        1. The `_id` refers to the `contenttype` id.
        2. The `_slug` refers to the lowercased name of the model.
        3. The `_count` refers to the number of instances bookmarked per type.

        See tags/tagged_models.html for how used."""
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
        """Each user may have bookmarked objects. This fetches all bookmarks made by a specific user."""
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
        """bookmarks tagged by the `user` with a `tag_slug`. The resulting queryset can be of different models since the `bookmark` model is generic; but if `content_id` is set, the instances must be of the same contenttype model represented by the `content_id`."""
        qs = self._bookmarker_by_user(user).filter(tags=tag)
        if content_id:
            qs = qs.filter(
                content_type=ContentType.objects.get_for_id(content_id)
            )
        return qs
