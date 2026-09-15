"""Portable adaptation of the project's four-frame OpenCLIP extractor.

This release uses an explicit manifest and local checkpoint. It is not the
historical cache format or the full competition inference pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MODALITIES = {"IR", "Depth", "Depth_Color", "Thermal"}
CONFIG = {"model": "ViT-B-32", "frames": 4, "sheet_size": [1300, 248],
          "padding": "square-black", "release": "portfolio-v1"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_frames(sheet):
    """Retain the historical crop geometry, then pad each 320x240 tile."""
    from PIL import ImageOps

    if sheet.size != (1300, 248):
        raise ValueError(f"Expected a 1300x248 four-frame sheet, got {sheet.size}")
    return [ImageOps.pad(sheet.crop((4 + 324 * i, 4, 324 + 324 * i, 244)),
                         (320, 320), color="black") for i in range(4)]


def load_manifest(path: Path):
    entries = json.loads(path.read_text())
    if not isinstance(entries, list) or not entries:
        raise ValueError("Manifest must be a nonempty JSON list")
    seen = set()
    parsed = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"clip_id", "modality", "path"}:
            raise ValueError("Each entry requires only clip_id, modality, and path")
        if not isinstance(entry["clip_id"], str) or not entry["clip_id"].strip():
            raise ValueError("clip_id must be a nonempty string")
        if entry["modality"] not in MODALITIES:
            raise ValueError("Only declared non-RGB modalities are accepted")
        key = (entry["clip_id"], entry["modality"])
        if key in seen:
            raise ValueError(f"Duplicate clip/modality: {key}")
        seen.add(key)
        source = path.parent / entry["path"]
        if not source.is_file():
            raise FileNotFoundError(source)
        parsed.append((entry, source))
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--device", default="cpu", choices=("cpu", "mps", "cuda"))
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if not args.checkpoint.is_file():
        parser.error("--checkpoint must name an existing local checkpoint")
    if args.output.exists():
        parser.error("Output already exists; choose a new path to preserve it")
    entries = load_manifest(args.manifest)

    import numpy as np
    import open_clip
    import torch
    from PIL import Image

    model, _, preprocess = open_clip.create_model_and_transforms(
        CONFIG["model"], pretrained=str(args.checkpoint.resolve()), device=args.device)
    model.eval()
    features = []
    source_hashes = []
    for entry, source in entries:
        source_hashes.append(file_sha256(source))
        with Image.open(source) as sheet:
            frames = [preprocess(frame) for frame in split_frames(sheet.convert("RGB"))]
        encoded_frames = []
        for start in range(0, len(frames), args.batch_size):
            with torch.inference_mode():
                batch = torch.stack(frames[start:start + args.batch_size]).to(args.device)
                encoded = model.encode_image(batch)
                encoded = encoded / encoded.norm(dim=-1, keepdim=True).clamp_min(1e-8)
            encoded_frames.append(encoded.float().cpu().numpy())
        features.append(np.concatenate(encoded_frames))
    features = np.stack(features)
    if not np.isfinite(features).all():
        raise ValueError("Encoder produced non-finite features")
    provenance = {"config": CONFIG, "checkpoint_sha256": file_sha256(args.checkpoint),
                  "source_sha256": source_hashes,
                  "clip_ids": [entry["clip_id"] for entry, _ in entries],
                  "modalities": [entry["modality"] for entry, _ in entries]}
    signature = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as output:
        np.savez_compressed(output, frames=features.astype(np.float16),
                            provenance=json.dumps(provenance, sort_keys=True), signature=signature)
    print(json.dumps({"shape": list(features.shape), "signature": signature}))


if __name__ == "__main__":
    main()
