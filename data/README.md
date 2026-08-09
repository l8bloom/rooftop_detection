# Data layout

- `raw/` contains downloaded source imagery and is intentionally ignored by Git.
- `input/` will contain small, versioned study inputs such as selected building footprints.
- `interim/` may hold regenerable georeferenced chips and masks; it is ignored when created.

The source imagery used for this assessment must be described in the repository
documentation, including its provider, acquisition date, licence, CRS, and download URL.
