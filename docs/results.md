# Result confidence

This table summarizes the geometry quality signals stored in
[`outputs/roof_attributes.json`](../outputs/roof_attributes.json). The outline score is a
weighted selection heuristic, not a calibrated probability that the roof is correct:

`0.55 × SAM score + 0.15 × footprint precision + 0.20 × footprint coverage + 0.10 × footprint IoU`

Precision measures how much of the predicted roof lies inside the official footprint;
coverage measures how much of that footprint the prediction covers. The footprint is a
useful prompt and consistency check, but it is not pixel-level ground truth and can differ
from visible eaves.

| Building and overlay | Area (m²) | Outline score | SAM score | Precision | Coverage | Footprint IoU | Area ratio | Assessment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [5431645](../outputs/overlays/vienna-c2-5431645.png) | 2,037.37 | 0.823 | 0.855 | 0.744 | 0.911 | 0.590 | 1.376 | **Manual review** |
| [5404559](../outputs/overlays/vienna-c2-5404559.png) | 645.54 | 0.812 | 0.842 | 1.000 | 0.713 | 0.564 | 0.569 | **Manual review** |
| [5357776](../outputs/overlays/vienna-c2-5357776.png) | 975.48 | 0.947 | 0.920 | 1.000 | 0.999 | 0.913 | 1.028 | Strong |
| [5521477](../outputs/overlays/vienna-c2-5521477.png) | 712.22 | 0.970 | 0.954 | 1.000 | 1.000 | 0.949 | 1.038 | Strong |
| [5404264](../outputs/overlays/vienna-c2-5404264.png) | 732.03 | 0.904 | 0.884 | 0.939 | 0.987 | 0.791 | 1.135 | Acceptable |
| [5468479](../outputs/overlays/vienna-c2-5468479.png) | 595.39 | 0.836 | 0.777 | 0.873 | 1.000 | 0.776 | 1.266 | **Manual review** |
| [5455869](../outputs/overlays/vienna-c2-5455869.png) | 372.55 | 0.951 | 0.928 | 1.000 | 0.995 | 0.914 | 1.005 | Strong |
| [5291770](../outputs/overlays/vienna-c2-5291770.png) | 380.92 | 0.964 | 0.951 | 1.000 | 1.000 | 0.911 | 1.094 | Strong |
| [5383501](../outputs/overlays/vienna-c2-5383501.png) | 239.49 | 0.962 | 0.945 | 1.000 | 1.000 | 0.922 | 0.959 | Strong |
| [5716811](../outputs/overlays/vienna-c2-5716811.png) | 243.59 | 0.976 | 0.974 | 1.000 | 1.000 | 0.895 | 1.105 | Strong |

“Strong” means that all automatic checks passed and the outline score is at least 0.94.
“Acceptable” means that all checks passed with a lower outline score. “Manual review” is
the pipeline's `review_required` decision: SAM score below 0.80, precision or coverage below
0.85, or an area ratio outside 0.75–1.30.

These assessments apply only to the extracted 2D outline and projected area. Roof type and
material remain unknown, with confidence `0.0`, because the orthophoto and this baseline do
not support defensible classification of those attributes.
