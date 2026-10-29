# -*- coding: utf-8 -*-
"""Execute all notebooks in-place to embed outputs (nbclient + ipykernel)."""
import os, sys
import nbformat
from nbclient import NotebookClient

HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NB = os.path.join(HERE, "notebooks")

files = sorted(f for f in os.listdir(NB) if f.endswith(".ipynb"))
for f in files:
    path = os.path.join(NB, f)
    nb = nbformat.read(path, as_version=4)
    # notebooks run with repo root as cwd
    client = NotebookClient(nb, timeout=900, kernel_name="python3",
                            resources={"metadata": {"path": HERE}})
    print(f"executing {f} ...", flush=True)
    client.execute()
    nbformat.write(nb, path)
    n_err = sum(1 for c in nb.cells if c.cell_type == "code"
                and any(o.get("output_type") == "error" for o in c.get("outputs", [])))
    print(f"  done {f}  (cells with errors: {n_err})", flush=True)
print("ALL_NOTEBOOKS_EXECUTED")
