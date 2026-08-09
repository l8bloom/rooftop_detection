# Design and reasoning

I selected Vienna Orthofoto 2024 rather than Sentinel-2 or street imagery. Its 15 cm ground sampling distance resolves eaves and roof structures, it is top-down so occlusion is limited, it covers the selected 2.5 km tile, and it is openly licensed (CC BY 4.0). The image is paired with a JGW world file and EPSG:31256, making pixel-to-map conversion deterministic. Sentinel-2 is too coarse for individual roof boundaries; street imagery is incomplete and poorly suited to complete outlines.

The City of Vienna LOD0.4 building-part layer supplies ten stable targets. For each target the service reads only a padded raster window, derives a box prompt from the footprint bounds, and runs SAM2. The prompt is numeric; coloured vector overlays are never passed to the model. SAM's selected mask is vectorised in EPSG:31256, repaired, lightly simplified, measured in metres, then transformed to WGS84 for the JSON result.

`sam_predicted_iou` is SAM's candidate quality estimate. `footprint_overlap` is the proportion of the predicted polygon within a one-metre footprint buffer. `outline`/`area` confidence combine them: low overlap flags likely leakage but does not clip the image-derived eave boundary. This avoids treating a building-part footprint as ground truth roof geometry.

The source supports projected roof area and outline only. Roof slope, true 3D area, material, and condition are not asserted from a single RGB orthophoto. With more time I would fuse a contemporaneous DOM/DGM for height, slope and aspect; label a local roof-material classifier; review low-confidence masks; and use tiled embedding/batched prompts with a job queue for city-scale execution.
