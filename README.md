# Rooftop detection

This component extracts imagery-derived roof outlines for ten Vienna buildings. It uses the City of Vienna's 2024 true orthophoto (15 cm GSD, CC BY 4.0), official building-part footprints to identify/prompt targets, and local `facebook/sam2.1-hiera-large` segmentation on ROCm.

## Run

```bash
uv sync --dev
uv run rooftop-detection prepare --config configs/vienna_c2.toml
uv run rooftop-detection detect --config configs/vienna_c2.toml
```

`prepare` embeds the JPEG world file and EPSG:31256 into an ignored GeoTIFF. `detect` reads the original JPEG in small windows, runs SAM2 once for each target, and writes committed deliverables:

- `outputs/roof_attributes.json` — WGS84 roof geometries, native-metre areas, provenance, and confidence.
- `outputs/overlays/*.png` — review imagery. Red is the mask and yellow is its vector boundary.

The source JPEG/JGW are committed so reviewers can inspect the exact inputs and reproduce GeoTIFF preparation without an additional download. The SAM2 model is loaded from the local Hugging Face cache, so inference uses no network. On this host use ROCm device 0 (the 24 GiB Radeon RX 7900 XTX).

## Scope and limits

The 15 cm nadir imagery supports roof outlines and projected area. It does **not** reliably reveal slope, true 3D roof area, material, or structural condition, so those are explicitly `unknown_from_top_down_rgb`. Footprints are prompts and quality signals, not hard clipping geometry: their building-part edges can differ from eaves.

See [the design note](docs/design.md) for source choice, confidence semantics, and the scaling plan.
