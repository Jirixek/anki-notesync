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
import re
import warnings
from copy import copy
from typing import NamedTuple

import anki.errors
from anki.collection import Collection
from anki.notes import Note
from aqt import mw
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)


def _show_synced_notes():
    # TODO: additional hook editor_did_load_note?
    # text field with clickable ids in menu bar
    pass


class Fetcher():
    TOKENS = [
        ('STARTIF', r'{{#.*?}}'),
        ('ENDIF', r'{{/.*?}}'),
        ('FIELD', r'{{.*?}}'),
        ('TEXT', r'.'),
    ]
    RE_TOKENS = re.compile('|'.join(f'(?P<{kind}>{value})' for kind, value in TOKENS), re.DOTALL)
    RE_FIELD = re.compile(r'{{(?P<field>[^:]+?)(?P<type>:\w*)?}}')
    RE_CLOZE = re.compile(r'{{c\d+::(.*?)(::.*?)?}}', re.DOTALL)
    RE_CLOZE_OVERLAPPER = re.compile(r'\[\[oc\d+::(.*?)(::.*?)?\]\]', re.DOTALL)
    RE_ASSUMPTION_HINT = re.compile(r'\[\[(.*?)(::.+?)?\]\]')
    RE_EQ_IM_HINT = re.compile(r'(.*?)(::.*)?', re.DOTALL)

    template_cache = {}

    def __init__(self, this_note: Note, other_note: Note):
        self.this_note = this_note
        self.other_note = other_note
        self.other_notetype = self.other_note.note_type()['name']
        try:
            if self.other_notetype not in self.template_cache:
                with open(os.path.join(os.path.dirname(__file__),
                                       f'./user_files/templates/{self.other_notetype}.html'), 'r') as f:
                    self.template_cache[self.other_notetype] = self.tokenize(f.read())
        except IOError:
            raise ValueError('Unknown model')

    @classmethod
    def __strip_cloze(cls, text: str):
        # TODO: nested clozes (add rust function)
        return Fetcher.RE_CLOZE.sub(r'\1', text)

    @classmethod
    def __strip_cloze_overlapping(cls, text: str):
        # TODO: nested clozes
        return Fetcher.RE_CLOZE_OVERLAPPER.sub(r'\1', text)

    @classmethod
    def __strip_assumption_hints(cls, text: str):
        return Fetcher.RE_ASSUMPTION_HINT.sub(r'\1', text)

    @classmethod
    def __strip_im_eq_hints(cls, text: str):
        return Fetcher.RE_EQ_IM_HINT.sub(r'\1', text)

    def __check_cycles(self, text_other: str):
        bs = BeautifulSoup(text_other, 'html.parser')
        spans = bs.find_all('span', {'class': 'sync', 'note': True}, recursive=False)
        for span in spans:
            other_id = span.get('note')
            if other_id == str(self.this_note.id):
                raise ValueError('Cycle detected')
        return text_other

    def __fetch_field(self, field: str):
        text = self.other_note[field]
        return self.__check_cycles(text)

    def __fetch_cloze_field(self, field: str):
        text = self.__strip_cloze(self.other_note[field])
        return self.__check_cycles(text)

    def __fetch_cloze_overlapping_field(self, field: str):
        text = self.__strip_cloze_overlapping(self.other_note[field])
        return self.__check_cycles(text)

    def __fetch_assumptions_field(self, field: str):
        text = self.__strip_assumption_hints(self.other_note[field])
        return self.__check_cycles(text)

    def __fetch_im_eq_hint_field(self, field: str):
        text = self.__strip_im_eq_hints(self.other_note[field])
        return self.__check_cycles(text)

    class Token(NamedTuple):
        type: str
        value: str

    @classmethod
    def tokenize(cls, template):
        tokens = []
        text = ''
        for m in cls.RE_TOKENS.finditer(template):
            kind = m.lastgroup
            value = m.group()

            if kind != 'TEXT' and len(text) > 0:
                tokens.append(Fetcher.Token('TEXT', text))
                text = ''

            if kind == 'STARTIF':
                tokens.append(Fetcher.Token(kind, value[3:-2]))
            elif kind == 'ENDIF':
                tokens.append(Fetcher.Token(kind, value[3:-2]))
            elif kind == 'FIELD':
                m = cls.RE_FIELD.fullmatch(value)
                m_field = m.group('field')
                m_type = m.group('type')
                if m_type == ':cloze':
                    tokens.append(Fetcher.Token('FIELD_CLOZE', m_field))
                elif m_type == ':cloze_overlapping':
                    tokens.append(Fetcher.Token('FIELD_CLOZE_OVERLAPPING', m_field))
                elif m_type == ':assumptions':
                    tokens.append(Fetcher.Token('FIELD_ASSUMPTIONS', m_field))
                elif m_type == ':with_im_eq_hint':
                    tokens.append(Fetcher.Token('FIELD_IM_EQ_HINT', m_field))
                else:
                    tokens.append(Fetcher.Token('FIELD_NORMAL', m_field))
            elif kind == 'TEXT':
                text += value

        if len(text) > 0:
            tokens.append(Fetcher.Token('TEXT', text))

        return tokens

    def fetch(self):
        out = '\n'
        skip = ''
        for token in self.template_cache[self.other_notetype]:
            if skip != '' and (token.type != 'ENDIF' or token.value != skip):
                continue

            if token.type == 'STARTIF':
                if self.__fetch_field(token.value) == '':
                    skip = token.value
            elif token.type == 'ENDIF':
                skip = ''
            elif token.type == 'FIELD_NORMAL':
                out += self.__fetch_field(token.value)
            elif token.type == 'FIELD_CLOZE':
                out += self.__fetch_cloze_field(token.value)
            elif token.type == 'FIELD_CLOZE_OVERLAPPING':
                out += self.__fetch_cloze_overlapping_field(token.value)
            elif token.type == 'FIELD_ASSUMPTIONS':
                out += self.__fetch_assumptions_field(token.value)
            elif token.type == 'FIELD_IM_EQ_HINT':
                out += self.__fetch_im_eq_hint_field(token.value)
            elif token.type == 'TEXT':
                out += token.value

        return BeautifulSoup(out, 'html.parser')


def sync_field(col: Collection, this_note: Note, field_idx: int) -> bool:
    # - find span with class 'sync' with 'note' attribute
    # - fetch optional 'fields' attribute (can contain special fields: text)
    # - or use defaults depending on the target note type)
    #   - EQ/IM: copy assumptions and text
    #   - Cloze [overlapper]: copy text
    #   - Algos: copy text, input, and output
    # - strip {{c1::}} and [[oc1::]]

    # TODO: support selection of fields to sync
    # multi_valued_attributes={'*': ['class', 'fields']}

    if this_note.id == 0:
        return False  # the card is being created
    if field_idx < 0 or field_idx >= len(this_note.values()):
        return False  # should not happen

    changed = False
    bs = BeautifulSoup(this_note.values()[field_idx], 'html.parser')

    # recursive=False: transitive references are not propagated (only top spans are synced)
    spans = bs.find_all('span', {'class': 'sync', 'note': True}, recursive=False)
    for span in spans:
        other_id = span.get('note')
        if other_id is None:
            continue

        span_new = copy(span)
        span_new.clear()
        try:
            other_note = col.get_note(int(other_id))
            # other_fields = span.get('fields')
            bs_new = Fetcher(this_note, other_note).fetch()
            span_new.append(bs_new)
        except (ValueError, anki.errors.NotFoundError) as e:
            div = bs.new_tag('div')
            if str(e) in {'Unknown model', 'Cycle detected'}:
                div.string = str(e)
            else:
                div.string = 'Invalid note ID'
            span_new.append(div)

        if span != span_new:
            span.replace_with(span_new)
            changed = True

    if changed:
        this_note.values()[field_idx] = bs.encode(formatter='html5').decode('utf-8')
        col.update_note(this_note)
    return changed


def sync_note(col: Collection, note: Note) -> bool:
    changed = False
    for field in note.keys():
        changed |= sync_field(col, note, note._field_index(field))
    return changed


def sync_all(col: Collection) -> int:
    n_changed = 0
    ids = col.find_notes('"*:*<span class=\\"sync\\" note=*"')
    for note_id in ids:
        note = col.get_note(note_id)
        changed = sync_note(col, note)
        if changed:
            n_changed += 1
    return n_changed
