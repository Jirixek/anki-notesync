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

import anki.collection  # isort:skip # noqa: F401
from anki.notes import Note
from aqt import gui_hooks, mw

from . import bidir, unidir


def on_editor_did_unfocus_field(changed: bool, note: Note, field_idx: int) -> bool:
    # return True if changes were made, otherwise return changed
    changed |= unidir.sync_field(mw.col, note, field_idx)
    changed |= bidir.sync_field(mw.col, note, field_idx)
    return changed


def on_sync_will_start():
    unidir.sync_all(mw.col)


gui_hooks.editor_did_unfocus_field.append(on_editor_did_unfocus_field)
gui_hooks.sync_will_start.append(on_sync_will_start)
