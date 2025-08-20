# Copyright (C) 2024 Jiří Szkandera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re

import pytest

from . import bidir
from .test_utils import get_empty_col, load_notes


@pytest.fixture
def col():
    return get_empty_col()


class MockPopup():
    def __init__(self, return_value: str):
        self.return_value = return_value
        self._n_called = 0

    def __call__(self, _):
        self._n_called += 1
        return self.return_value

    def n_called(self):
        return self._n_called


def test_download_single(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n2, 0)

    assert bidir.sync_field(col, n2, 0, MockPopup('Download')) is True
    load_notes((n1, n2))

    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_download_multiple(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    n3 = col.new_note(basic)
    n3['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n3, 0)

    assert bidir.sync_field(col, n3, 0, MockPopup('Download')) is True
    load_notes((n1, n2, n3))

    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n3['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_upload_single(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n2, 0)

    assert bidir.sync_field(col, n2, 0, MockPopup('Upload')) is True
    load_notes((n1, n2))

    assert n1['Front'] == '<span class="sync" sid="1">New content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">New content</span>'


def test_upload_multiple(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    n3 = col.new_note(basic)
    n3['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n3, 0)

    assert bidir.sync_field(col, n3, 0, MockPopup('Upload')) is True
    load_notes((n1, n2, n3))

    assert n1['Front'] == '<span class="sync" sid="1">New content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">New content</span>'
    assert n3['Front'] == '<span class="sync" sid="1">New content</span>'


def test_download_different_ids(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">ID1</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="2">ID2</span>'
    col.add_note(n2, 0)

    assert bidir.sync_field(col, n2, 0, MockPopup('Download')) is False
    load_notes((n1, n2))

    assert n1['Front'] == '<span class="sync" sid="1">ID1</span>'
    assert n2['Front'] == '<span class="sync" sid="2">ID2</span>'


def test_upload_different_ids(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">ID1</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="2">ID2</span>'
    col.add_note(n2, 0)

    assert bidir.sync_field(col, n2, 0, MockPopup('Upload')) is False
    load_notes((n1, n2))

    assert n1['Front'] == '<span class="sync" sid="1">ID1</span>'
    assert n2['Front'] == '<span class="sync" sid="2">ID2</span>'


def test_download_single_card(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    assert bidir.sync_field(col, n1, 0, MockPopup('Download')) is False
    load_notes((n1,))

    assert n1['Front'] == '<span class="sync" sid="1">Content</span>'


def test_upload_single_card(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    assert bidir.sync_field(col, n1, 0, MockPopup('Upload')) is False
    load_notes((n1,))

    assert n1['Front'] == '<span class="sync" sid="1">Content</span>'


def test_no_change(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    popup = MockPopup('Download')

    assert bidir.sync_field(col, n2, 0, popup) is False
    load_notes((n1, n2))

    assert popup.n_called() == 0
    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_empty_span_always_downloaded(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1"></span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    popup = MockPopup('Download')

    assert bidir.sync_field(col, n1, 0, popup) is True
    load_notes((n1, n2))

    assert popup.n_called() == 0
    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_change_popup(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Garbage</span>'
    col.add_note(n2, 0)

    popup = MockPopup('Download')

    assert bidir.sync_field(col, n2, 0, popup) is True
    load_notes((n1, n2))

    assert popup.n_called() == 1


def test_span_coherency_homogenous(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    assert bidir.are_spans_coherent(col, [n1.id, n2.id], 1) is True


def test_span_coherency_non_homogenous(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    n3 = col.new_note(basic)
    n3['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n3, 0)

    assert bidir.are_spans_coherent(col, [n1.id, n2.id, n3.id], 1) is False


def test_card_is_being_created(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1"></span>'

    assert bidir.sync_field(col, n2, 0, MockPopup('Download')) is False
    # No exception raised


def test_dont_change_spans_without_class(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span sid="1"></span>'
    col.add_note(n2, 0)

    assert bidir.sync_field(col, n2, 0, MockPopup('Download')) is False
    load_notes((n1, n2))

    assert n2['Front'] == '<span sid="1"></span>'


def test_id_missing(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync">Content</span>'
    col.add_note(n1, 0)

    assert bidir.sync_field(col, n1, 0, MockPopup('Download')) is True
    load_notes((n1,))

    assert re.fullmatch(f'<span class="sync" sid="{n1.id}_0_' + r'\d{4}' + '">Content</span>', n1['Front'])


def test_id_missing_multiple_spans_in_note(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = (
        '<span class="sync" sid="1">Content</span>'
        '<span class="sync">Another</span>'
    )
    col.add_note(n1, 0)

    assert bidir.sync_field(col, n1, 0, MockPopup('Download')) is True
    load_notes((n1,))

    print(n1['Front'])
    assert re.fullmatch((
        f'<span class="sync" sid="1">Content</span>'
        f'<span class="sync" sid="{n1.id}_0_' + r'\d{4}' + '">Another</span>'
    ), n1['Front'])

# TODO
# def test_nested_spans():
#     pass

# def test_inside_single_card():
#     pass
