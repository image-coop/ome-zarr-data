# FLIM dataset

Dataset from the study:

https://doi.org/10.1111/jmi.70036

Obtained from BioImage Archive:

https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD1967

And used with permission. License is CC-BY.

Direct download to this specific image:

https://ftp.ebi.ac.uk/biostudies/fire/S-BIAD/967/S-BIAD1967/Files/lifetime_separation/study_component_embryos/TMR31_3_sptw.7z

The raw data has been downscaled and rechunked to produce the zarr file, using `flim-data-downscale.py`.

This dataset can also be accessed directly with https at:

```
https://test-bucket.image.coop/rfc3/flim-tmr31-3-reduced64.ome.zarr
```

A script to load this dataset into napari can be found at this gist:

https://gist.github.com/jni/d188d9778a4f3a3318c34256ee2b6e2e

or you can install napari>=0.9.0 and napari-ome-zarr>=0.10.0 and run:

```
napari --plugin napari-ome-zarr https://test-bucket.image.coop/rfc3/flim-tmr31-3-reduced64.ome.zarr
```
