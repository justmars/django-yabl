from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import BadRequest
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.safestring import SafeText
from django.utils.text import slugify
from django_extensions.db.models import TimeStampedModel

from .managers import MarkedTags, UserAnnotations
from .utils import (
    ADD_TAGS,
    DEL_TAG,
    GET_ITEM,
    LAUNCH_MODAL,
    LIST_BOOKMARKED,
    LIST_FILTERED,
    LIST_TAGS,
    MODAL_BASE,
    PANEL,
    TOGGLE_STATUS,
    Pathmaker,
)


class TagItem(TimeStampedModel):
    name = models.SlugField(max_length=100)

    # managers
    objects = models.Manager()
    tagged = UserAnnotations()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created"]

    @classmethod
    def set_context(cls, user, tag_slug: str, model_id: Optional[int] = None):
        """The `tag_slug` (and optional `model_id`) from url refer to objects requesting `user` has previously tagged. If user is not authenticated, show empty list."""
        context = {}
        if model_id:
            context["model_type"] = ContentType.objects.get_for_id(model_id)
        tag = get_object_or_404(TagItem, name=tag_slug)
        extract = Bookmark.objects_tagged.extract_from
        context["user_tagged_objs"] = extract(user, tag, model_id)
        return context


class Bookmark(TimeStampedModel):
    # main fields
    bookmarker = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    tags = models.ManyToManyField(TagItem, related_name="bookmarked")

    # generic fk base
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=250)  # allows UUID
    content_object = GenericForeignKey("content_type", "object_id")

    # managers
    objects = models.Manager()
    objects_tagged = MarkedTags()

    def __str__(self):
        return f"{self.bookmarker} saved {self.content_object}"


class AbstractBookmarkable(models.Model):
    bookmarks = GenericRelation(
        Bookmark, related_query_name="%(app_label)s_%(class)ss"
    )

    class Meta:
        abstract = True

    def make_action_url(self, act: str):
        base = f"{self._meta.app_label}:{act}_{self._meta.model_name}"
        return reverse(base, args=(self.pk,))

    @cached_property
    def launch_modal_url(self):
        return self.make_action_url(LAUNCH_MODAL)

    @cached_property
    def get_item_url(self):
        return self.make_action_url(GET_ITEM)

    @cached_property
    def add_tags_url(self):
        return self.make_action_url(ADD_TAGS)

    @cached_property
    def del_tag_url(self):
        return self.make_action_url(DEL_TAG)

    @cached_property
    def toggle_status_url(self):
        return self.make_action_url(TOGGLE_STATUS)

    @property
    def modal(self) -> SafeText:
        """Return html with htmx modal launcher based on app_name. Presumes prior coordination with bookmarks.utils in urls.py"""
        raw = """<em hx-trigger="click"
                hx-get="{url}"
                hx-target="body"
                hx-swap="beforeend"
                hx-indicator="#{loader_id}"
                _="on mouseover add [@style=text-decoration:underline] to me
                    on mouseleave remove [@style=text-decoration:underline] from me
                "
                >view</em>
                <span id="{loader_id}" class="spinner-border spinner-border-sm htmx-indicator" role="status">
                    <span class="visually-hidden">Loading...</span>
                </span>
            """
        return format_html(
            raw, loader_id=f"spinner-{self.pk}", url=self.launch_modal_url
        )

    @property
    def object_content_for_panel(self) -> SafeText:
        """Displayed at the top of the tag PANEL."""
        raw = "<h2>Must be overriden by {{model_name}}'s properties.</h2>"
        return format_html(raw, model_name=self._meta.model_name)

    def set_bookmarked_context(self, user) -> dict:
        """The tag PANEL in bookmarks/utils.py requires the use of certain variables that will not change, e.g. `is_bookmarked`, `toggle_url`. The values that fill these constants however will change based on the object instance `obj` and the `user` that is passed to this method."""
        return {
            "object": self,
            "object_content_for_panel": self.object_content_for_panel,
            "is_bookmarked": self.is_bookmarked(user),
            "user_tags": self.get_user_tags(user),
            "toggle_url": self.toggle_status_url,
            "add_tags_url": self.add_tags_url,
            "del_tag_url": self.del_tag_url,
        }

    def is_bookmarked(self, user) -> bool:
        """Has `user` bookmarked to this object instance?"""
        return self.bookmarks.filter(bookmarker=user).exists()

    def get_bookmarked(self, user) -> Optional[Bookmark]:
        """Get instance bookmarked to by the `user`."""
        if not self.is_bookmarked(user):
            return None
        return self.bookmarks.get(bookmarker=user)

    def get_user_tags(self, user) -> QuerySet:
        """If user bookmarked, get `user`-made tags on instance."""
        if bookmark := self.get_bookmarked(user):
            return bookmark.tags.all()
        return []

    def toggle_bookmark(self, user) -> bool:
        """If `user` is bookmarked to the instance, unbookmark; otherwise, bookmark."""
        if not self.is_bookmarked(user):
            return self._bookmark_this(user)
        return self._unbookmark_this(user)

    def _unbookmark_this(self, user) -> bool:
        """Implies `user` already bookmarked to the instance. This removes the `bookmark` object from the instance's `bookmarks` field."""
        bookmark = self.get_bookmarked(user)
        self.bookmarks.remove(bookmark)
        if tags := self.get_user_tags(user):
            tags.delete()
        return self.is_bookmarked(user)  # status after unbookmarking

    def _bookmark_this(self, user) -> bool:
        """Implies `user` is not yet bookmarked to the instance. This add a `bookmark` object to the instance's `bookmarks` field."""
        bookmark = Bookmark(content_object=self, bookmarker=user)
        self.bookmarks.add(bookmark, bulk=False)
        return self.is_bookmarked(user)  # status after bookmark

    def add_tags(self, user, tags_to_add: list[str]):
        """Parse a list of `tags_to_add`, by a `user` to an auto-bookmarked model instance."""
        if not self.is_bookmarked(user):  # auto-bookmark
            self._bookmark_this(user)

        bookmark = self.bookmarks.get(bookmarker=user)
        _existing = list(bookmark.tags.values_list("name", flat=True))
        for input_name in tags_to_add:
            slug = slugify(input_name)
            if slug not in _existing:
                tag_obj, _ = TagItem.objects.get_or_create(name=slug)
                bookmark.tags.add(tag_obj)

    def remove_tag(self, user, tag_to_remove: str):
        """Since bookmarked instance can have existing tags, enable user to remove an existing tag name."""
        slug = slugify(tag_to_remove)
        tag_to_remove = get_object_or_404(TagItem, name=slug)

        if not self.is_bookmarked(user):  # auto-bookmark
            self._bookmark_this(user)

        bookmark = self.bookmarks.get(bookmarker=user)
        if bookmark.tags.filter(name=slug).exists():
            bookmark.tags.remove(tag_to_remove)

    @classmethod
    def launch_modal_func(
        cls, request: HttpRequest, pk: str
    ) -> TemplateResponse:
        """Launches the modal containing tagging and bookmarking functions"""
        if not request.method == "GET":
            raise BadRequest
        if not request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_URL)

        obj = get_object_or_404(cls, pk=pk)
        panel = {"content_template": PANEL}
        context = obj.set_bookmarked_context(request.user) | panel
        return TemplateResponse(request, MODAL_BASE, context)

    @classmethod
    def get_item_func(
        cls,
        request: HttpRequest,
        pk: str,
        user_slug: Optional[str] = None,
    ):
        """Launches the object containing tagging and bookmarking functions"""
        if not request.method == "GET":
            raise BadRequest

        obj = get_object_or_404(cls, pk=pk)
        context = {}
        if user_slug:
            if user_found := get_object_or_404(
                get_user_model(), username=user_slug
            ):
                context = obj.set_bookmarked_context(user_found)
        else:
            if request.user.is_authenticated:
                context = obj.set_bookmarked_context(request.user)
        return TemplateResponse(request, PANEL, context)

    @classmethod
    def toggle_status_func(
        cls, request: HttpRequest, pk: str
    ) -> TemplateResponse:
        """Toggles the requesting user's preference re: bookmarked status of the object"""
        if not request.method == "PUT":
            return HttpResponseRedirect(settings.LOGIN_URL)
        if not request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_URL)

        obj = get_object_or_404(cls, pk=pk)
        obj.toggle_bookmark(request.user)
        context = obj.set_bookmarked_context(request.user)
        return TemplateResponse(request, PANEL, context)

    @classmethod
    def add_tags_func(cls, request: HttpRequest, pk: str) -> TemplateResponse:
        """Auto-bookmarks and tags the object with the submitted POST input form"""
        if not request.method == "POST":
            raise BadRequest
        if not request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_URL)

        obj = get_object_or_404(cls, pk=pk)
        if submitted := request.POST.get("tags"):
            if add_these := submitted.split(","):
                obj.add_tags(request.user, add_these)
        context = obj.set_bookmarked_context(request.user)
        return TemplateResponse(request, PANEL, context)

    @classmethod
    def del_tag_func(cls, request: HttpRequest, pk: str) -> HttpResponse:
        """Deletes a previously added user-made tag of a specific object"""
        if not request.method == "DELETE":
            raise BadRequest
        if not request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_URL)

        obj = get_object_or_404(cls, pk=pk)
        if delete_this := request.POST.get("tag"):
            obj.remove_tag(request.user, delete_this)
        return HttpResponse(headers={"HX-Trigger": "tagDeleted"})
