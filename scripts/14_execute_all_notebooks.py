"""Execute every notebook in notebooks/ so the committed files carry real outputs."""

import glob
import os
import sys
import traceback

import nbformat
from nbclient import NotebookClient

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NBDIR = os.path.join(BASE, "notebooks")

results = []
for path in sorted(glob.glob(os.path.join(NBDIR, "*.ipynb"))):
    name = os.path.basename(path)
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=420,
        kernel_name="python3",
        allow_errors=True,
        resources={"metadata": {"path": BASE}},
    )
    try:
        client.execute()
        errs = [
            o for c in nb.cells if c.cell_type == "code"
            for o in c.get("outputs", []) if o.get("output_type") == "error"
        ]
        imgs = sum(
            1 for c in nb.cells if c.cell_type == "code"
            for o in c.get("outputs", []) if "image/png" in o.get("data", {})
        )
        outs = sum(len(c.get("outputs", [])) for c in nb.cells if c.cell_type == "code")
        nbformat.write(nb, path)
        results.append((name, "ok", outs, imgs, len(errs)))
        print(f"{name:48s} ok   outputs={outs:3d} images={imgs:2d} errors={len(errs)}")
        for o in errs[:1]:
            print("   last error:", (o.get("ename") or "")[:80])
    except Exception as exc:  # kernel crash / timeout
        results.append((name, "FAIL", 0, 0, 1))
        print(f"{name:48s} FAIL {type(exc).__name__}: {str(exc)[:120]}")
        traceback.print_exc(limit=1)

print("\nsummary:", len(results), "notebooks")
bad = [r for r in results if r[1] != "ok" or r[4] > 0]
print("with problems:", [r[0] for r in bad] or "none")
sys.exit(1 if bad else 0)
