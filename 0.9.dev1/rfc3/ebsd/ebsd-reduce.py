#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = "==3.12.*"
# dependencies = [
#     "numpy==2.5.*",
#     "zarr==3.2.*",
#     "h5py==3.16.*",
#     "dask[array]==2026.6.0",
# ]
# ///
"""
This script downscales original EBSD data provided by Jie Luo, Ethan Sprague,
and Michael Preuss from Monash University.

Original h5oina[1]_ file available at:

    https://www.dropbox.com/scl/fi/sdf72pk9qtq5zur4ofj2l/CP-Ti-abnormal-grains-spec-1-site-5.h5oina?rlkey=gpqg19n3ifkd24rgkkwjs3dwv&dl=1

Then run this script pointed the h5oina file and the desired output directory,
eg:

    uv run ebsd-reduce.py \
            ~/Downloads/CP-Ti-abnormal-grains-spec-1-site-5.h5oina \
            data/CP-Ti-abnormal-grains-reduced-144x.zarr/s0

"""
import argparse
from pathlib import Path
import numpy as np
from dask import array as da
import h5py

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path, help='Path to the input zarr array.')
parser.add_argument('output', type=Path, help='Path to the output zarr array.')
args = parser.parse_args()

fn = args.input.expanduser().as_posix()
fnout = args.output.expanduser()
fnout.mkdir(parents=True, exist_ok=True)
fnout = fnout.as_posix()

f = h5py.File(fn)

ebsd = f['1/EBSD']
pat = ebsd['Data/Processed Patterns']  # array, (npatterns, dy, dx)
nx = ebsd['Header/X Cells'][0]  # patterns are along 2D scan
ny = ebsd['Header/Y Cells'][0]

pat2d = da.from_array(pat, chunks=pat.chunks).reshape(
        (ny, nx) + pat.shape[-2:]
        )
reduced = da.coarsen(
    np.mean,
    pat2d,
    dict(zip(range(4), [2, 2, 6, 6])),
    trim_excess=True,
    ).astype(np.uint8)
reduced.rechunk((15, 17) + reduced.chunksize[2:]).to_zarr(fnout)
