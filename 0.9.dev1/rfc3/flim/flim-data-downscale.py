#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = "==3.12.*"
# dependencies = [
#     "numpy==2.5.*",
#     "zarr==3.2.*",
#     "dask[array,diagnostics]==2026.6.0",
#     "rechunker @ git+https://github.com/pangeo-data/rechunker.git@refs/pull/161/head",
# ]
# ///
"""
This script downscales original raw data from BioImage Archive by summing
detections from adjacent pixels.

Full study: https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD1967

Download original dataset from BioImage Archive:

    https://ftp.ebi.ac.uk/biostudies/fire/S-BIAD/967/S-BIAD1967/Files/lifetime_separation/study_component_embryos/TMR31_3_sptw.7z

Then unzip, and run this script pointed the zarr directory and the desired
output directory, eg

    uv run flim-data.py \
            ~/Downloads/TMR31_3_sptw/TMR31_3_sptw.zarr \
            data/flim-tmr31-3-reduced64.ome.zarr/s0

Data is from this study:

    https://doi.org/10.1111/jmi.70036
"""
import argparse
from pathlib import Path
import tempfile
import numpy as np
import zarr
from dask import array as da
from dask.diagnostics import ProgressBar
from rechunker import rechunk

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path, help='Path to the input zarr array.')
parser.add_argument('output', type=Path, help='Path to the output zarr array.')
args = parser.parse_args()

fn = args.input.expanduser().as_posix()
fnout = args.output.expanduser().as_posix()

# read array
z = da.from_zarr(fn)

# take every 4th time point
skipt = z[:, :, ::4]

# coarsen by summing nearby photon counts
coarsened = da.coarsen(
        np.sum, skipt, {1: 2, 3: 2, 4: 2, 5: 2}, trim_excess=True
        ).astype(np.uint8)

# set output parameters
chunk_shape = (1, 70, 1, 19, 128, 128)
shard_shape = tuple(  # single shard for ease of sharing
        map(int,
            np.ceil(np.array(coarsened.shape) / np.array(chunk_shape))
            * np.array(chunk_shape)
            )
        )
codec = None
store_out = zarr.create_array(
        fnout,
        shape=coarsened.shape,
        shards=shard_shape,
        chunks=chunk_shape,
        dtype=np.uint8,
        )

with tempfile.TemporaryDirectory(suffix='.zarr') as tmpdir:
    plan = rechunk(
            coarsened,
            chunk_shape,
            int(4e9),
            fnout,
            temp_store=tmpdir,
            )
    with ProgressBar():
        plan.execute()
