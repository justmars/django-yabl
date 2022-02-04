import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeText

from bookmarks.models import AbstractBookmarkable


class SampleBook(AbstractBookmarkable):
    """Used for testing only. See bookmarks/tests/conftest.py"""

    title = models.CharField(max_length=50)
    excerpt = models.TextField(null=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Book"  # see generic relations, e.g. content_type.name
        verbose_name_plural = "Books"

    def __str__(self) -> str:
        return (
            f"{self.title} by {self.author.first_name} {self.author.last_name}"
        )

    def get_absolute_url(self):
        return reverse("examples:book_detail", kwargs={"pk": self.pk})

    @property
    def object_content_for_panel(self) -> SafeText:
        return format_html(
            """
            <h2>{title}</h2>
            <h3>{author}</h3>
            <p>{excerpt}</p>
            """,
            title=self.title,
            excerpt=self.excerpt,
            author=f"{self.author.first_name} {self.author.last_name}",
        )


class SampleQuote(AbstractBookmarkable):
    """Used for testing only. See bookmarks/tests/conftest.py"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    book = models.ForeignKey(
        SampleBook, on_delete=models.CASCADE, related_name="quotes"
    )
    quote = models.TextField()

    class Meta:
        verbose_name = "Quote"  # see generic relations, e.g. content_type.name
        verbose_name_plural = "Quotes"

    def __str__(self) -> str:
        return f"{self.quote[:50]}"

    @property
    def object_content_for_panel(self) -> SafeText:
        return format_html(
            """
            <figure>
                <blockquote>{quote}</blockquote>
                <center>
                    <figcaption>
                    {author}, <cite title="{book_title}">{book_title}</cite>
                    </figcaption>
                </center>
            </figure>
            """,
            book_title=self.book.title,
            quote=self.quote,
            author=f"{self.book.author.first_name} {self.book.author.last_name}",
        )
