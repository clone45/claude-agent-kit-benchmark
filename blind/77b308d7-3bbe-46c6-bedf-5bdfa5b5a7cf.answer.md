The decision is made in `should_strip_ansi`, called from `echo`. Explicit `color` wins; otherwise codes are stripped unless the stream is a TTY or a Jupyter kernel stream.

- **Call site:** `src/click/utils.py`, `echo()`, line 330: `elif should_strip_ansi(file, resolve_color_default(color)): out = strip_ansi(out)`. It only runs for `str` output. Bytes go straight to the binary stream and are never stripped (lines 320–327). Empty output just flushes and returns early.
- **Input 1, the stream:** `file`, or by default `_default_text_stdout()` / `_default_text_stderr()` when `err=True` (`echo`, lines 287–291).
- **Input 2, the color flag:** `src/click/globals.py`, `resolve_color_default()`, lines 54–67. It returns the `color=` argument passed to `echo` if it isn't `None`. Otherwise it returns the current context's `ctx.color`. With no context it returns `None`.
- **The rule:** `src/click/_compat.py`, `should_strip_ansi(stream, color)`, lines 502–513.
  1. If `color` is not `None`, return `not color`, so an explicit True/False always wins.
  2. If `color` is `None` and the stream is `None`, `sys.stdin` is checked in its place.
  3. If the stream has a `color` attribute, which is the pager's `_PagerWriter` that handles stripping itself, return `False`.
  4. Otherwise, strip when `not isatty(stream) and not _is_jupyter_kernel_output(stream)`.
- **Helpers in `_compat.py`:**
  - `isatty()`, lines 540–544, calls `stream.isatty()` and treats any exception as `False`.
  - `_is_jupyter_kernel_output()`, lines 495–499, unwraps `_FixupStream` / `_NonClosingTextIOWrapper` and checks whether the class's module starts with `ipykernel.`.
  - `strip_ansi()`, lines 491–492, removes every match of `_ansi_re` (line 19). That regex matches any ECMA-48 CSI sequence, not just the SGR codes Click emits.

In short, colors are kept when the caller or context forces them on, or when output goes to a terminal, a Jupyter kernel or the pager. Otherwise they're stripped, for example for files, pipes and `StringIO`.