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

import os
from typing import Sequence

import pytest
from anki.notes import Note

from . import unidir
from .test_utils import get_empty_col, load_notes


@pytest.fixture
def col():
    return get_empty_col()


def test_sync_cloze(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'


def test_sync_n_clozes(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}} {{c2::two}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'


def test_sync_cloze_hints(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::hint}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'


def test_sync_n_clozes_hints(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::h1}} {{c2::two::h2}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'


def test_nbsp(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one&nbsp;two}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one&nbsp;two</div>\n</span>'


def test_changed(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '<div class="first-upper">cringeis&nbsp;cringe.</div>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = (
        f'<span class="sync" note="{n1.id}">\n'
        '<div><div class="first-upper">cringeis&nbsp;cringe.</div></div>\n'
        '</span>'
    )
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is False


def test_invalid_target_id_int(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="1234"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == '<span class="sync" note="1234"><div>Invalid note ID</div></span>'


def test_invalid_target_id_string(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="foo"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == '<span class="sync" note="foo"><div>Invalid note ID</div></span>'


def test_card_is_being_created(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'

    assert unidir.sync_field(col, n2, 0) is False
    # No exception raised


def test_invalid_arg_field_id(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="foo"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 42) is False
    # No exception raised


def test_dont_change_spans_without_note_attribute(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is False
    load_notes((n1, n2))

    assert n2['Front'] == '<span class="sync"></span>'


def test_dont_change_spans_without_sync_class(col):
    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is False
    load_notes((n1, n2))

    assert n2['Front'] == f'<span note="{n1.id}"></span>'


@pytest.mark.skipif(not os.path.isfile('./user_files/templates/EQ.html'), reason='Eq.html exists')
@pytest.mark.parametrize('with_context', [False, True])
@pytest.mark.parametrize('with_assumptions', [False, True])
class TestImEq():
    def fill_im_eq_note(self, note: Note, with_context: bool,
                        with_assumptions: bool, hint_fields: Sequence[str]):
        hint_fields_set: set[str] = set(hint_fields)
        for key in note.keys():
            if key in hint_fields_set:
                note[key] = f'{key}::Hint {key}'
            else:
                note[key] = str(key)

        context_expected_str = (
            '<div id=\"context\">'
            '<ol><li>Context1</li><li>Longer context2</li></ol>'
            '</div>\n'
        )
        if with_context:
            note['Context'] = '<ol><li>Context1</li><li>Longer context2</li></ol>'
            context_expected = context_expected_str
        else:
            note['Context'] = ''
            context_expected = ''

        assumptions_expected_str = (
            '<div class=\"assumptions-body\" id=\"assumptions\">'
            '<ol><li>Assumption1</li><li>Before assumption2</li></ol>'
            '</div>\n'
        )
        if with_assumptions:
            note['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::Hint Assumptions]]</li></ol>'
            assumptions_expected = assumptions_expected_str
        else:
            note['Assumptions'] = ''
            assumptions_expected = ''

        self.context_container_expected = (
            '<div class=\"context-container\">\n' +
            context_expected +
            assumptions_expected +
            '</div>\n'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('EQ1', 'EQ2')])
    def test_eq(self, col, with_context: bool, with_assumptions: bool, hint_fields: Sequence[str]):
        eq = col.models.by_name('EQ')
        basic = col.models.by_name('Basic')

        n1 = col.new_note(eq)
        self.fill_im_eq_note(n1, with_context, with_assumptions, hint_fields)
        col.add_note(n1, 0)

        n2 = col.new_note(basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        col.add_note(n2, 0)

        assert unidir.sync_field(col, n2, 0) is True
        load_notes((n1, n2))

        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.context_container_expected +
            f'<div class="first-upper">EQ1{n1["Delimiter"]}EQ2.</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('EQ1', 'EQ2')])
    def test_eq_tex(self, col, with_context: bool, with_assumptions: bool, hint_fields: Sequence[str]):
        m = col.models.by_name('EQ (TEX)')
        basic = col.models.by_name('Basic')

        n1 = col.new_note(m)
        self.fill_im_eq_note(n1, with_context, with_assumptions, hint_fields)
        col.add_note(n1, 0)

        n2 = col.new_note(basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        col.add_note(n2, 0)

        assert unidir.sync_field(col, n2, 0) is True
        load_notes((n1, n2))

        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.context_container_expected +
            f'<div>\\[EQ1 {n1["Delimiter"]} EQ2\\]</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('Cloze')])
    def test_im(self, col, with_context: bool, with_assumptions: bool, hint_fields: Sequence[str]):
        m = col.models.by_name('IM')
        basic = col.models.by_name('Basic')

        n1 = col.new_note(m)
        self.fill_im_eq_note(n1, with_context, with_assumptions, hint_fields)
        col.add_note(n1, 0)

        n2 = col.new_note(basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        col.add_note(n2, 0)

        assert unidir.sync_field(col, n2, 0) is True
        load_notes((n1, n2))

        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.context_container_expected +
            f'<div class="first-upper">{n1["Context Left"]}Cloze.</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('Cloze Left', 'Cloze Right')])
    def test_im_reversed(self, col, with_context: bool, with_assumptions: bool, hint_fields: Sequence[str]):
        m = col.models.by_name('IM (reversed)')
        basic = col.models.by_name('Basic')

        n1 = col.new_note(m)
        self.fill_im_eq_note(n1, with_context, with_assumptions, hint_fields)
        col.add_note(n1, 0)

        n2 = col.new_note(basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        col.add_note(n2, 0)

        assert unidir.sync_field(col, n2, 0) is True
        load_notes((n1, n2))

        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.context_container_expected +
            f'<div class="first-upper">{n1["Context Left"]}Cloze Left{n1["Context Middle"]}Cloze Right.</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('Cloze Left', 'Cloze Right')])
    @pytest.mark.parametrize('model', ['IM (TEX)', 'IM (TEX, reversed)'])
    def test_im_tex(self, col, model, with_context: bool, with_assumptions: bool, hint_fields: Sequence[str]):
        m = col.models.by_name(model)
        basic = col.models.by_name('Basic')

        n1 = col.new_note(m)
        self.fill_im_eq_note(n1, with_context, with_assumptions, hint_fields)
        col.add_note(n1, 0)

        n2 = col.new_note(basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        col.add_note(n2, 0)

        assert unidir.sync_field(col, n2, 0) is True
        load_notes((n1, n2))

        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.context_container_expected +
            f'<div>\\[Cloze Left {n1["Delimiter"]} Cloze Right\\]</div>\n'
            '</span>'
        )


def test_unknown_note_type(col):
    basic = col.models.by_name('Basic')

    models = col.models
    unknown = models.new('Foo')
    models.add_field(unknown, models.new_field('Front'))
    template = models.new_template('Template 1')
    template["qfmt"] += '{{Front}}'
    template["afmt"] += '{{Front}}'
    models.add_template(unknown, template)
    models.add_dict(unknown)

    unknown = col.models.by_name('Foo')
    n1 = col.new_note(unknown)
    n1['Front'] = 'one'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == f'<span class="sync" note="{n1.id}"><div>Unknown model</div></span>'


def test_cycles(col):
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    col.add_note(n1, 0)
    n2 = col.new_note(cloze)
    n2['Text'] = f'Before2 <span class="sync" note="{n1.id}"></span> After2'
    col.add_note(n2, 0)
    n1['Text'] = f'Before1 <span class="sync" note="{n2.id}"></span> After1'
    col.update_note(n1)

    assert unidir.sync_field(col, n1, 0) is True
    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n1['Text'] == f'Before1 <span class="sync" note="{n2.id}"><div>Cycle detected</div></span> After1'
    assert n2['Text'] == f'Before2 <span class="sync" note="{n1.id}"><div>Cycle detected</div></span> After2'


def test_span_containing_html_elements(col):
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = 'Front1 <b>Front bold</b> Front2'
    n1['Back'] = 'Back1 <b>Back bold</b> Back2'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    load_notes((n1, n2))

    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n'
        '<div>\n'
        '  Front1 <b>Front bold</b> Front2\n'
        '  <hr>\n'
        '  Back1 <b>Back bold</b> Back2\n'
        '</div>\n'
        '</span>')


def test_field_excluded_from_unqualified_search(col):
    basic = col.models.by_name('Basic (with back excluded from unqualified search)')

    n1 = col.new_note(basic)
    n1['Back'] = 'Text on the back'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Back'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_all(col) == 1
    load_notes((n1, n2))

    assert n2['Back'] == (
        f'<span class="sync" note="{n1.id}">\n'
        '<div>\n'
        '<hr>\n'
        '  Text on the back\n'
        '</div>\n'
        '</span>'
    )
