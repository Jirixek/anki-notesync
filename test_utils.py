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
import shutil
import tempfile
from typing import Sequence

from anki.collection import Collection
from anki.notes import Note

# Creating new decks is expensive. Just do it once, and then spin off
# copies from the master.
_empty_col: str | None = None


def _create_custom_notes(col: Collection):
    CUSTOM_NOTES = {
        'EQ': ('EQ1', 'Delimiter', 'EQ2', 'Context', 'Assumptions'),
        'EQ (TEX)': ('EQ1', 'Delimiter', 'EQ2', 'Context', 'Assumptions'),
        'IM': ('Context Left', 'Cloze', 'Context', 'Assumptions'),
        'IM (reversed)': ('Context Left', 'Cloze Left', 'Context Middle', 'Cloze Right', 'Context', 'Assumptions'),
        'IM (TEX)': ('Cloze Left', 'Delimiter', 'Cloze Right', 'Context', 'Assumptions'),
        'IM (TEX, reversed)': ('Cloze Left', 'Delimiter', 'Cloze Right', 'Context', 'Assumptions'),
    }

    for name, fields in CUSTOM_NOTES.items():
        models = col.models
        model = models.new(name)
        template = models.new_template('Template 1')
        for field in fields:
            models.add_field(model, models.new_field(field))
            template["qfmt"] += '{{' + field + '}}'
            template["afmt"] += '{{' + field + '}}'
        models.add_template(model, template)
        models.add_dict(model)


def _create_note_with_field_excluded_from_unqualified_search(col: Collection):
    models = col.models
    model = models.new('Basic (with back excluded from unqualified search)')
    template = models.new_template('Template 1')

    front_field = models.new_field('Front')
    back_field = models.new_field('Back')
    back_field["excludeFromSearch"] = True

    models.add_field(model, front_field)
    models.add_field(model, back_field)

    template["qfmt"] = '{{ Front }}'
    template["afmt"] = '{{ Front }} | {{ Back }}'

    models.add_template(model, template)
    models.add_dict(model)


def get_empty_col():
    global _empty_col
    if not _empty_col:
        (fd, path) = tempfile.mkstemp(suffix='.anki2')
        os.close(fd)
        os.unlink(path)
        col = Collection(path)
        _create_custom_notes(col)
        _create_note_with_field_excluded_from_unqualified_search(col)
        col.close(downgrade=False)
        _empty_col = path
    (fd, path) = tempfile.mkstemp(suffix='.anki2')
    shutil.copy(_empty_col, path)
    col = Collection(path)
    return col


def load_notes(notes: Sequence[Note]):
    for note in notes:
        note.load()
