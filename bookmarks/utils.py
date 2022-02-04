from ast import Call
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
Placed here for easier access in configuration and tests)
"""

MODAL_BASE = "commons/modal.html"
PANEL = "commons/_panel.html"
ITEM = "commons/item.html"
LIST_BOOKMARKED = "bookmarks/bookmark_objs.html"
LIST_TAGS = "tags/list_of_tags.html"
LIST_FILTERED = "tags/filtered_objs.html"

"""
URLS
"""


@dataclass
class Pathmaker:
    """Auto-generate patterns with the convention `{act}_{model_klass._meta.model_name}` from view functions with respect to: (a) launching a modal inspecting a specific `obj` instance of a `model_klass`  (b) adding / deleting tags within the panel with respect to such `obj` instance; and (c) bookmarking / unbookmarking the `obj`."""

    model_klass: Model
    launch_func: Callable
    get_item_func: Callable
    add_tags_func: Callable
    del_tag_func: Callable
    toggle_status_func: Callable

    def make_patterns(self) -> list[URLPattern]:
        return [  # fake implies we don't know the value of the arg yet
            self.uniform_act_path(LAUNCH_MODAL, self.launch_func, fake=True),
            self.uniform_act_path(LAUNCH_MODAL, self.launch_func),
            self.uniform_act_path(GET_ITEM, self.get_item_func, fake=True),
            self.uniform_act_path(GET_ITEM, self.get_item_func),
            self.uniform_act_path(ADD_TAGS, self.add_tags_func),
            self.uniform_act_path(DEL_TAG, self.del_tag_func),
            self.uniform_act_path(TOGGLE_STATUS, self.toggle_status_func),
        ]

    def uniform_act_path(
        self, act: str, func: Callable, fake: bool = False
    ) -> URLPattern:
        """
        Given parameters for launching the modal with a view, produces the following path:
        - `route` = samplebook/launch_modal
        - `view` = launch_func (the function object Callable, not its return)
        - `name` = launch_modal_samplebook (the combiation of act and model name)

        Note nuance addition: fake urls imply the need to make the url dynamic such as when a modal url will only be filled up with an identifier during runtime or when it's necessary to setup the base url before adding from the ORM.
        """
        model_name = self.model_klass._meta.model_name
        route = f"{model_name}/{act}/"
        if not fake:
            route += "<str:pk>"
        return path(route=route, view=func, name=f"{act}_{model_name}")
