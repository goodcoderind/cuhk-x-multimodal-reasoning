# Primary sources and acknowledgments

Links reviewed on 15 September 2026. Model names distinguish actual checkpoint families; mentioning a paper does not mean its complete training recipe was reproduced.

## CUHK-X

- [A Large-Scale Multimodal Dataset and Benchmarks for Human Activity Scene Understanding and Reasoning](https://arxiv.org/abs/2512.07136) — the dataset and benchmark paper.
- [Official CUHK-X repository](https://github.com/openaiotlab/CUHK-X) and [current license](https://github.com/openaiotlab/CUHK-X/blob/main/LICENSE) — source, attribution and data terms.
- [Large Model Track rules](https://www.kaggle.com/competitions/cuhk-x-competition-large-model-track/rules) — participation, data use and public code sharing.
- [Official UbiComp/ISWC challenge page](https://www.ubicomp.org/ubicomp-iswc-2026/cuhk-x-competition/) — track definitions, current schedule and verification process.

CUHK-X was created by the **AIoT Lab, Department of Information Engineering, The Chinese University of Hong Kong**. This portfolio is independent of the organizers.

## Visual encoders

| Component | Primary source | License information reviewed |
| --- | --- | --- |
| OpenCLIP implementation | [mlfoundations/open_clip](https://github.com/mlfoundations/open_clip) | [MIT license](https://github.com/mlfoundations/open_clip/blob/main/LICENSE) |
| Exact historical frame checkpoint | [LAION CLIP ViT-B/32, laion2B-s34B-b79K](https://huggingface.co/laion/CLIP-ViT-B-32-laion2B-s34B-b79K) | Model card identifies MIT; also read its intended-use limitations |
| V-JEPA 2 implementation | [facebookresearch/vjepa2](https://github.com/facebookresearch/vjepa2) | [MIT license](https://github.com/facebookresearch/vjepa2/blob/main/LICENSE); check any separately licensed portions |
| Exact native64 checkpoint | [facebook/vjepa2-vitl-fpc64-256](https://huggingface.co/facebook/vjepa2-vitl-fpc64-256) | Model card identifies MIT |
| R(2+1)D-18 | [torchvision model documentation](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.video.r2plus1d_18.html) | Consult upstream software and weight terms separately |
| InternVideo2-S14 research source | [OpenGVLab/InternVideo](https://github.com/OpenGVLab/InternVideo) | Consult the exact source/checkpoint terms; no code or weights from this model are bundled here |

The OpenCLIP model card credits Romain Beaumont and the LAION/OpenCLIP contributors. V-JEPA 2 is work by FAIR at Meta; its model card supplies the research citation. Their pretrained representations are upstream contributions, not models trained from scratch by this project.

The independent public prediction baseline and AI-assisted development are credited separately in [ATTRIBUTION.md](ATTRIBUTION.md). The optional extractor's implementation boundary is described in [research/README.md](../research/README.md).
