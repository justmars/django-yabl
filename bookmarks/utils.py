from dataclasses import dataclass
from typing import Callable

from django.db.models import Model
from django.urls import URLPattern, path

"""
ACTIONS
Used in models.py and in the urls.py by the convenience dataclass declared below.
"""
ADD_TAGS = "add_tags"
DEL_TAG = "del_tag"
TOGGLE_STATUS = "toggle_status"
LAUNCH_MODAL = "launch_modal"
GET_ITEM = "get_item"


"""
TEMPLATES
Placed here for easier access in configuration and tests
"""

MODAL_BASE = "commons/modal.html"
"""Skeleton template of the modal"""

PANEL = "commons/_panel.html"
"""Content and action panel which will hold the tag form, tag list with delete badges, and the bookmarking toggle"""

LIST_BOOKMARKED = "bookmarks/bookmark_list.html"
"""Contains a list of all bookmarked objects"""

LIST_TAGS = "tags/tag_list.html"
"""Contains a list of all tags used in bookmarked objects"""

LIST_FILTERED = "tags/filter_objects_by_tag_model.html"
"""Lists down bookmarked objects of the user filtered through their tags"""

"""
URLS
"""


@dataclass
class Pathmaker:
    """Auto-generate patterns with the convention `{act}_{model_klass._meta.model_name}` from view functions with respect to: (a) launching a modal inspecting a specific `obj` instance of a `model_klass`  (b) adding / deleting tags within the panel with respect to such `obj` instance; and (c) bookmarking / unbookmarking the `obj`."""

    model_klass: Model

    def make_patterns(self) -> list[URLPattern]:
        return [
            # get_item urls
            self.make_path(GET_ITEM, self.model_klass.get_item_func),
            self.add_user(GET_ITEM, self.model_klass.get_item_func),
            # launch_modal urls; the value of arg unknown when declared, may be supplied during runtime
            self.make_path(
                LAUNCH_MODAL, self.model_klass.launch_modal_func, is_fake=True
            ),
            self.make_path(LAUNCH_MODAL, self.model_klass.launch_modal_func),
            # add tags url
            self.make_path(ADD_TAGS, self.model_klass.add_tags_func),
            # del tag url
            self.make_path(DEL_TAG, self.model_klass.del_tag_func),
            # toggle bookmark url
            self.make_path(TOGGLE_STATUS, self.model_klass.toggle_status_func),
        ]

    def add_user(self, act: str, func: Callable) -> URLPattern:
        """Same as make_path() but with a special parameter in the route for possible user"""
        model_name = self.model_klass._meta.model_name
        path_name = f"{act}_{model_name}"
        route = f"{model_name}/{act}/<str:pk>/<slug:user_slug>"
        return path(route=route, view=func, name=path_name)

    def make_path(
        self, act: str, func: Callable, is_fake: bool = False
    ) -> URLPattern:
        """
        Given parameters for launching the modal with a view, produces the following path:
        - `route` = samplebook/launch_modal
        - `view` = launch_func (the function object Callable, not its return)
        - `name` = launch_modal_samplebook (the combiation of act and model name)

        Note nuance addition: fake urls imply the need to make the url dynamic such as when a modal url will only be filled up with an identifier during runtime or when it's necessary to setup the base url before adding from the ORM.
        """
        model_name = self.model_klass._meta.model_name
        route = f"{model_name}/{act}"
        if not is_fake:
            route += "/<str:pk>"
        return path(route=route, view=func, name=f"{act}_{model_name}")
