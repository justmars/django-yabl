from django.urls.resolvers import URLPattern

from bookmarks.utils import Pathmaker
from examples.models import SampleBook
from examples.views import (
    add_tags_samplebook,
    del_tag_samplebook,
    launch_modal_samplebook,
    toggle_status_samplebook,
)


def test_Pathmaker_patterns():
    s = Pathmaker(
        model_klass=SampleBook,
        launch_func=launch_modal_samplebook,
        toggle_status_func=toggle_status_samplebook,
        add_tags_func=add_tags_samplebook,
        del_tag_func=del_tag_samplebook,
    )
    patterns = s.make_patterns()
    assert len(patterns) == 5
    for path in patterns:
        assert isinstance(path, URLPattern)
