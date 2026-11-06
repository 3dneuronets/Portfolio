"""Load fixed human L2/3 positions and directed edges for NetPyNE.

Position-file row number (0-based) is the network GID, PROVIDED that
populations are created in POP_ORDER and cells retain file order.
The external ID in the fifth column is metadata, not a NetPyNE GID.
"""
from collections import Counter, defaultdict
from math import isfinite
from pathlib import Path

POP_ORDER = ('HL23PYR', 'HL23SST', 'HL23PV', 'HL23VIP')
TYPE_MAP = {
    'PYR': 'HL23PYR',
    'SST': 'HL23SST',
    'PV': 'HL23PV',
    'VIP': 'HL23VIP',
}


def read_positions(path):
    rows = []
    external_ids = set()
    for line_no, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split()
        if not fields or fields[0].startswith('#'):
            continue
        if len(fields) != 5:
            raise ValueError(f'{path}:{line_no}: expected x y z TYPE external_id')
        x, y, z = map(float, fields[:3])
        if not all(map(isfinite, (x, y, z))):
            raise ValueError(f'{path}:{line_no}: non-finite coordinate')
        if fields[3] not in TYPE_MAP:
            raise ValueError(f'{path}:{line_no}: unknown cell type {fields[3]!r}')
        ext_id = fields[4]  # Keep as text: these large IDs are NOT indices/GIDs.
        if ext_id in external_ids:
            raise ValueError(f'{path}:{line_no}: repeated external ID {ext_id}')
        external_ids.add(ext_id)
        rows.append({'x': x, 'y': y, 'z': z,
                     'pop': TYPE_MAP[fields[3]], 'external_id': ext_id})

    if not rows:
        raise ValueError(f'No cells in {path}')

    # Both files in this project use the same explicit global row-index order.
    groups = []
    for row in rows:
        if not groups or groups[-1] != row['pop']:
            groups.append(row['pop'])
    if tuple(groups) != POP_ORDER:
        raise ValueError(f'Position rows are not grouped as expected: {groups}')
    return rows


def population_layout(rows):
    counts = Counter(row['pop'] for row in rows)
    starts = {}
    offset = 0
    for pop in POP_ORDER:
        starts[pop] = offset
        offset += counts[pop]
    assert offset == len(rows)
    return {pop: counts[pop] for pop in POP_ORDER}, starts


def netpyne_cell_lists(rows, frame='model', center_x=250.0,
                       center_z=250.0, top_y=-550.0):
    """Map file somata to population-specific cellsList values.

    frame='model': ONLY translate the whole cloud (preserve all relative
    distances and axes); center the x/z ranges on (center_x, center_z)
    and put the largest source y at top_y. This matches the current model's
    negative Y depth convention and existing 500 x 500 horizontal box.

    frame='native': retain the literal x/y/z from the .dat file. If using
    native, update network dimensions and all electrode coordinates too.
    """
    if frame not in ('model', 'native'):
        raise ValueError('frame must be model or native')

    mid_x = (min(r['x'] for r in rows) + max(r['x'] for r in rows)) / 2.0
    mid_z = (min(r['z'] for r in rows) + max(r['z'] for r in rows)) / 2.0
    max_y = max(r['y'] for r in rows)

    min_x = min(r['x'] for r in rows)
    min_y = min(r['y'] for r in rows)
    min_z = min(r['z'] for r in rows)

    cells = {p: [] for p in POP_ORDER}
    for gid, r in enumerate(rows):
        if frame == 'model':
            x = r['x'] - min_x
            y = r['y'] - min_y
            z = r['z'] - min_z
        else:
            x, y, z = r['x'], r['y'], r['z']
        # Keep this list ordered, to preserve the expected GID mapping.
        cells[r['pop']].append({'x': float(x), 'y': float(y), 'z': float(z),
                                'sourceIndex': gid, 'sourceID': r['external_id']})
    return cells


def read_unique_edges(path, n_cells):
    """Each unique directed pair becomes ONE biological connection.

    Duplicated rows do NOT generate additional contacts; n_cont in the
    spreadsheet will be applied to each unique pair in connParams.
    """
    pairs = []
    seen = set()
    duplicates = 0
    for line_no, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split()
        if not fields or fields[0].startswith('#'):
            continue
        if line_no == 1 and [f.lower() for f in fields] == ['pre', 'post']:
            continue
        if len(fields) != 2:
            raise ValueError(f'{path}:{line_no}: expected pre post')
        pre, post = map(int, fields)
        if not (0 <= pre < n_cells and 0 <= post < n_cells):
            raise ValueError(f'{path}:{line_no}: invalid pair {(pre, post)}')
        if pre == post:
            raise ValueError(f'{path}:{line_no}: self-connection {(pre, post)}')
        pair = (pre, post)
        if pair in seen:
            duplicates += 1
            continue
        seen.add(pair)
        pairs.append(pair)
    return pairs, duplicates


def population_conn_lists(rows, pairs):
    """Return (pre-pop, post-pop) -> population-RELATIVE connList entries."""
    _, starts = population_layout(rows)
    groups = defaultdict(list)
    for pre, post in pairs:
        pre_pop, post_pop = rows[pre]['pop'], rows[post]['pop']
        groups[(pre_pop, post_pop)].append([
            pre - starts[pre_pop], post - starts[post_pop]
        ])
    return groups
