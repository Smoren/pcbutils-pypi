import pytest
from pcbutils.structs import Pin, Side


def test_news_repo():
    pin = Pin(side=Side.BOTH, x=0, y=0, outer_radius=3, inner_radius=2)
    assert 1 == 1
