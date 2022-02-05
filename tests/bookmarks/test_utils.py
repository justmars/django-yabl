from django.urls.resolvers import URLPattern

from bookmarks.utils import Pathmaker
from examples.models import SampleBook


def test_Pathmaker_patterns():
    s = Pathmaker(SampleBook)
    patterns = s.make_patterns()
    assert len(patterns) == 7
    for path in patterns:
        assert isinstance(path, URLPattern)
