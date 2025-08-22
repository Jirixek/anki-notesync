# Anki Notesync plugin

This is an Anki addon that synchronizes content across multiple notes.
To see the source code, request a feature, or report a bug, visit the GitHub repository [here](https://github.com/Jirixek/anki-notesync).

## Usage

There are two modes of synchronization: unidirectional and bidirectional.

### Unidirectional mode

To use the unidirectional mode, first retrieve a note ID of a note.
This can be done using Ctrl+Shift+I shortcut in the browser.

To include the content of a note on another note, use the following syntax.

```html
<span class="sync" note="1702531901010">
   content
</span>
```

The block needs to be inserted in a raw form into the card.
Use Ctrl-Shift-X when focused on the field to insert raw HTML.

Inside the plugin's folder, there is `user_files/templates` folder containing templates used for generating the content.
Content in a sync block is generated based on the type of *source* note.
For the default Anki note types, examples are provided inside the folder.
For custom note types, add a new template file with the name of a note type.

The sync blocks are synchronized when the field is unfocused and when a collection is synchronized.
As there is a single source of truth, no conflicts can arise.

### Bidirectional mode

To use the bidirectional mode, wrap the content inside a sync element like this.
Again, the wrapping has to be done inside the window editing the raw text.

```html
<span class="sync">
   content
</span>
```

A unique sync ID is generated for the sync block when the field is unfocused.

```html
<span class="sync" sid="1655457568076_2_8406">
   content
</span>
```

To reference the content on another note, insert the span block where necessary.

```html
<span class="sync" sid="1655457568076_2_8406"></span>
```

The sync blocks are synchronized when the field is unfocused.
In case of a conflict, either a pop-up is shown requesting a resolution,
or the contents of a sync block are uploaded to other sync blocks in a collection.
The behavior can be controlled by setting `bidir_unfocus_action` value in
the plugin's config to `ask` or `upload`, respectively.

### Example config

Below is an example plugin config.

```json
{
    "bidir_unfocus_action": "upload"
}
```
