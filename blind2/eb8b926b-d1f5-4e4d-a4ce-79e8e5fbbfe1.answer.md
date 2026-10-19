The decision is a fixed chain of checks, all in `src/modules/PianoRoll/PianoRollEditorWidget.hpp` unless noted:

1. **`onButton`** (1624–1643): a left-button press calls `beginDrag(e.pos, e.mods)`.
2. **`beginDrag`** (1889–1948): `zoneAt` (1387) picks the area under the pointer, and `ZONE_GRID` goes on to `beginGridDrag(position, shift)`.
3. **`beginGridDrag`** (2032–2121) tries each case in turn, and the first match wins:
   - **A. Shift held** (2047): toggles whether the note is selected, or starts a marquee.
   - **B. Inside the selection box** (`selectionBounds`, 1455, only when two or more notes are selected): starts a move. Edges are never tested here, so a note in a group can't be resized.
   - **C. `edgeGrabAt`** (1422–1451): if it hits, sets `DRAG_RESIZE` with `drag_left_edge = grab.left_edge` (2078–2091).
   - **D. `noteIndexAt`** (1406): a hit on the note body calls `selectOnly` then `beginMove` (2095–2099).
   - **E/F.** Empty grid: clears the selection if a box is up, otherwise paints a new note.
4. **Grab zone**, in `edgeGrabAt`: notes are scanned from the top of the list down, on the pointer's pitch row. The zone is `min(EDGE_GRAB_W, max(1, width/3))` pixels on either side of an edge (1439). `EDGE_GRAB_W` is 4 px (`PianoRollGeometry.hpp:127`), so notes 12 px or wider get ±4 px, narrower ones get ±width/3, with a 1 px floor. This shrinking keeps a narrow note from being all edge, so it can still be moved.
5. **Right edge first**: for each note, the right edge `x1` is tested before the left edge `x0` (1441), so it wins any overlap.
6. **Short-note left edge**: the left edge only counts when the note is wider than `EDGE_GRAB_MIN_NOTE_W`, which is 4 × 2.5 = 10 px (1445, `PianoRollGeometry.hpp:128`). The comment's reason is that on a note that narrow, grabbing the left edge could be confused with grabbing the right. A press near the left edge of such a note misses step C and moves the note instead (D).
7. **Hover cursor**: `onHover` (1590–1601) runs the same order (box, then `edgeGrabAt`, then `noteIndexAt`, then empty). It ignores modifiers, so shift-click still shows the plain cursor.