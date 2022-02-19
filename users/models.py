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
        from examples.models import SampleBook

        return SampleBook.get_bookmarks_by_user(self)

    @property
    def saved_quotes(self):

        from examples.models import SampleQuote

        return SampleQuote.get_bookmarks_by_user(self)
