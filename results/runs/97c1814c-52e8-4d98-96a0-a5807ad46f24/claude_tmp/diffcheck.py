import importlib.util, inspect, itertools, random, sys
sys.path.insert(0, "src")
import click.termui as new
spec = importlib.util.spec_from_file_location("click._orig_termui", ".claude/tmp/termui_orig.py",
    submodule_search_locations=None)
orig = importlib.util.module_from_spec(spec); orig.__package__ = "click"; spec.loader.exec_module(orig)

def run(f, *a, **k):
    try: return ("ok", f(*a, **k))
    except Exception as e: return ("err", type(e), str(e))

colors = [None, "red", "bright_white", "reset", "nope", "", 0, 1, 255, 256, -1, True, False,
          (1, 2, 3), [0, 0, 255], (1, 2), (1, 2, 256), (True, 0, 0), (1.0, 2, 3), 3.0, b"red", object]
toggles = [None, True, False, 0, 1, "", "x"]
texts = ["hi", 42, None, b"x", ""]
n = 0
for fg, bg in itertools.product(colors, colors):
    for text in texts:
        for reset in (True, False):
            assert run(orig.style, text, fg, bg, reset=reset) == run(new.style, text, fg, bg, reset=reset), (fg, bg); n += 1
names = ["bold","dim","underline","overline","italic","blink","reverse","strikethrough"]
for vals in itertools.product(toggles[:3], repeat=8):
    kw = dict(zip(names, vals))
    assert run(orig.style, "t", **kw) == run(new.style, "t", **kw); n += 1
rnd = random.Random(0)
for _ in range(20000):
    kw = {k: rnd.choice(toggles) for k in names}
    a = ("t", rnd.choice(colors), rnd.choice(colors))
    assert run(orig.style, *a, **kw) == run(new.style, *a, **kw); n += 1
assert inspect.signature(orig.style) == inspect.signature(new.style)
assert orig.style.__annotations__ == new.style.__annotations__
assert orig.style.__doc__ == new.style.__doc__
print("equivalent over", n, "cases")
