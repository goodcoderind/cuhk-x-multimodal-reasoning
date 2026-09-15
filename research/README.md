# Optional frame-encoding example

`frame_clip.py` adapts the project's original `encode_frame_clip.py`. It retains the four-frame crop, square padding, frozen OpenCLIP encoding, and unit normalization. The public version replaces workspace-specific paths with a manifest, requires an explicit **local** checkpoint, records content hashes, and refuses to overwrite an existing output. Its output format is new; it is not a drop-in replacement for the competition cache.

The historical input was a 1300×248 contact sheet: four 320×240 tiles, a four-pixel margin, and four-pixel gaps. Each tile is cropped separately and padded to 320×320 before the model's transform. The format is intentionally strict; do not pass arbitrary collages.

Install optional dependencies in an isolated environment:

```bash
python -m pip install -r research/requirements.txt
```

Supply a manifest such as this **illustrative** example, with paths relative to the manifest file:

```json
[
  {"clip_id": "example_001", "modality": "IR", "path": "sheets/example_001_ir.jpg"},
  {"clip_id": "example_001", "modality": "Depth_Color", "path": "sheets/example_001_depth.jpg"}
]
```

```bash
python research/frame_clip.py \
  --manifest /path/to/local/manifest.json \
  --checkpoint /path/to/local/open_clip_pytorch_model.bin \
  --output /path/to/local/features.npz \
  --device cpu
```

Use a compatible ViT-B-32 checkpoint. The historical run used `laion2b_s34b_b79k`. Obtain weights through their official source and review their license separately. This repository includes neither weights nor competition media. Declaring a modality does not verify image provenance; the caller must supply permitted non-RGB inputs. Converting a depth or infrared image to three channels for the encoder does not turn it into ordinary RGB camera footage.

The output stores `[number_of_views, 4, embedding_dimension]` features with clip/modality identifiers and checkpoint/input hashes. This example does not train a classifier, select answers, or reproduce the leaderboard score. The release checks validate cropping on synthetic images; pretrained inference was not rerun during portfolio packaging.
