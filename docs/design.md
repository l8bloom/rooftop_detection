# Design and reasoning

## Source choice

I selected City of Vienna Orthofoto 2024 as the primary detection source. Its 15 cm ground sampling distance resolves individual eaves and roof structures; its true-orthophoto processing limits building lean; its nadir viewpoint avoids much of the façade occlusion present in street or oblique imagery; and one tile covers the complete study area. It is free open data under CC BY 4.0. The JPEG is paired with a JGW world file and the published EPSG:31256 CRS, making pixel-to-map conversion deterministic.

Sentinel-2 was rejected for outline extraction because 10 m pixels are far larger than the roof-boundary detail required here. Street and Mapillary imagery were not used because coverage and viewpoints are inconsistent and complete outlines are generally occluded. Oblique imagery could help identify façade-adjacent edges but would require camera calibration. Vienna height products are the strongest next source for slope and 3D area, but temporal alignment with the 2024 orthophoto must be checked before fusion.

The City of Vienna LOD0.4 building-part layer supplies ten stable target IDs. It is not treated as roof truth: cadastral/building-part boundaries can differ from visible eaves, and adjacent parts can touch while representing different building IDs.

## Detection and geolocation

The preparation stage embeds the JGW affine transform and EPSG:31256 into a tiled GeoTIFF. Detection validates the raster and vector CRS, reprojects targets when necessary, and reads only an eight-metre padded window for each building. The footprint bounds become SAM's box prompt; coloured review overlays are never model input.

SAM returns three mask candidates. Each is vectorised in the projected CRS, repaired, filtered below 3 m², simplified by 0.3 m and scored using SAM quality plus four footprint-relative signals: precision (leakage), coverage (omission), IoU and area ratio. Weak initial results receive a second inference containing positive points safely inside the footprint and negative points in bounding-box context/concavities. The best composite candidate is retained, but unresolved thresholds produce `review_required=true` rather than silent acceptance.

The final Polygon or MultiPolygon preserves detached components and interior courtyard rings. Area is measured in EPSG:31256 before transforming the complete geometry to EPSG:4326 longitude/latitude coordinates. The rendered overlay is rasterised from that same cleaned geometry, so it matches the JSON deliverable exactly.

## Attributes and confidence

The source reliably supports projected outline and plan area. It does not directly measure roof slope, height or true surface area. Material/type labels may be visually plausible for some buildings, but this baseline reports them as unknown with confidence 0 until a labelled classifier or explicit human review is introduced.

`sam_predicted_iou` is the model's internal candidate estimate. `footprint_precision`, `footprint_coverage` and `footprint_iou` are independent geometric checks against a one-metre-tolerant source footprint. `confidence.outline` is a documented composite quality score, while `confidence.area` is conservatively reduced because plan area inherits boundary uncertainty. These values are not empirically calibrated probabilities. They are operational signals for auto-accept, retry and manual-review routing.

## Scaling

At city scale I would spatially partition the GeoTIFF, query footprints by tile, batch similarly sized crops, cache image embeddings for prompt retries, and write idempotent jobs keyed by imagery/version/building ID. Low-quality or changed buildings would enter a review queue. Metrics would track latency, mask-quality distributions, failure reasons and drift by district/roof class. A labelled validation set—not footprint agreement alone—would calibrate thresholds and per-attribute confidence.

With more time I would add contemporaneous DOM/DGM fusion for slope/aspect/3D area, coarse roof-type/material classification, solar/superstructure detection, portable CPU/CUDA dependency profiles, and regression tests using frozen representative crops.
