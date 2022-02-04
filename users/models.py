from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return self.username

    def get_absolute_url(self):
        return reverse(
            "users:get_user_profile", kwargs={"username": self.username}
        )

    @property
    def saved_books(self):
        from bookmarks.models import Bookmark
        from examples.models import SampleBook

        ct = ContentType.objects.get(app_label="examples", model="samplebook")
        return SampleBook.objects.filter(
            id__in=list(
                Bookmark.objects.filter(
                    content_type=ct, bookmarker=self
                ).values_list("object_id", flat=True)
            )
        )

    @property
    def saved_quotes(self):
        from bookmarks.models import Bookmark
        from examples.models import SampleQuote

        ct = ContentType.objects.get(app_label="examples", model="samplequote")
        return SampleQuote.objects.filter(
            id__in=list(
                Bookmark.objects.filter(
                    content_type=ct, bookmarker=self
                ).values_list("object_id", flat=True)
            )
        )
