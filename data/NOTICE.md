# Data notice

Files under `data/annotations/`, `data/manifests/`, `data/splits/` and
`data/reference/` are **derived from third-party datasets** and are
redistributed under their original license, **CC BY-NC-SA 4.0**
(<https://creativecommons.org/licenses/by-nc-sa/4.0/>):

| Dataset | DOI | Authors |
|---|---|---|
| DataSEC | [10.5281/zenodo.17033970](https://doi.org/10.5281/zenodo.17033970) | Fredianelli L., Artuso F., Pompei G., Licitra G., Iannace G., Akbaba A. |
| DataSED | [10.5281/zenodo.15346092](https://doi.org/10.5281/zenodo.15346092) | Fredianelli L., Artuso F., Pompei G., Licitra G., Iannace G., Akbaba A. |

- `data/annotations/datased_*_events.csv` are the DataSED event annotations,
  re-serialised to a common schema (label mapping to this project's taxonomy
  added; original labels kept in `raw_class_label`).
- Manifests, splits, duplicate/exclusion lists and normalisation statistics
  are metadata computed by this project from those datasets.

Non-commercial use only; derivatives must be shared under the same license.
The audio itself is **not** included — download it from the DOIs above.

The PANNs CNN14 AudioSet checkpoint used for training (Zenodo record 3576403)
records no license, so it is not redistributed here.
