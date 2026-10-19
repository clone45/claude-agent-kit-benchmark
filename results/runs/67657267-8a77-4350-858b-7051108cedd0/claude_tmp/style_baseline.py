import itertools, sys
from click.termui import style, _ansi_colors

colors = [None, *_ansi_colors, "nope", "", 0, 1, 255, 256, -1, True, False, 3.0,
          (0, 0, 0), (255, 12, 128), [1, 2, 3], (1, 2), (1, 2, 256), (True, 0, 0),
          ("1", 2, 3), object]
out = []
def rec(**kw):
    try:
        out.append(repr(style("hi", **kw)))
    except Exception as e:
        out.append(f"{type(e).__name__}: {e}")
for fg, bg in itertools.product(colors, repeat=2):
    rec(fg=fg, bg=bg)
attrs = ["bold", "dim", "underline", "overline", "italic", "blink", "reverse", "strikethrough"]
for vals in itertools.product([None, True, False], repeat=len(attrs)):
    for reset in (True, False):
        rec(**dict(zip(attrs, vals)), reset=reset)
for v in (0, 1, "", "x"):
    rec(bold=v, dim=v, italic=v)
for text in (1, None, b"x", [1]):
    out.append(repr(style(text, fg="red")))
sys.stdout.write("\n".join(out) + "\n")
