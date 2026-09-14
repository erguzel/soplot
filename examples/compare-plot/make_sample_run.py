"""Redraw every plot in the notebook and save it under sample-run/.

The images are generated from the notebook's own cells rather than from a copy
of them, so the two cannot drift apart: change a cell, run this, and the picture
follows. Run it from this directory:

    python make_sample_run.py
"""

from __future__ import annotations

import ast
import json
import pathlib
import re

import matplotlib
import matplotlib.pyplot as plt
import seaborn.objects as so

# no display: the figures go straight to disk
matplotlib.use('Agg')

HERE = pathlib.Path(__file__).parent
NOTEBOOK = HERE / 'compare-plot.ipynb'
OUTPUT = HERE / 'sample-run'


def slug(title: str) -> str:
    """Turn a markdown heading into a file name."""
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def save(result: object, path: pathlib.Path) -> bool:
    """Draw whatever a cell returned, if it is something that can be drawn."""
    if isinstance(result, so.Plot):
        figure = plt.figure(figsize=(7, 4), layout='tight')
        result.on(figure).plot()
    elif isinstance(result, matplotlib.figure.Figure):
        figure = result
    else:
        return False
    figure.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(figure)
    return True


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
    namespace: dict[str, object] = {'__name__': '__main__'}
    heading = 'plot'
    written: set[pathlib.Path] = set()

    for cell in notebook['cells']:
        source = ''.join(cell['source'])
        if cell['cell_type'] == 'markdown':
            titles = [line for line in source.splitlines() if line.startswith('## ')]
            if titles:
                heading = titles[-1].removeprefix('## ')
            continue

        # a cell ending in an expression is a cell that shows something: run the
        # statements, then evaluate that last expression to get the object back
        tree = ast.parse(source)
        tail = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
        exec(compile(tree, str(NOTEBOOK), 'exec'), namespace)
        if tail is None:
            continue
        result = eval(compile(ast.Expression(tail.value), str(NOTEBOOK), 'eval'), namespace)

        path = OUTPUT / f'{slug(heading)}.png'
        if save(result, path):
            written.add(path)
            print(f'wrote {path.relative_to(HERE)}')

    # a renamed heading would otherwise leave its old picture behind, and a
    # stale picture is worse than a missing one
    for stale in sorted(set(OUTPUT.glob('*.png')) - written):
        stale.unlink()
        print(f'removed {stale.relative_to(HERE)}')


if __name__ == '__main__':
    main()
