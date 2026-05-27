# Marine Debris Detection from Sentinel-2 Imagery
## Multi-Scale Spectral Index Fusion via DeepSpectralUNet

**Blekinge Institute of Technology — Deep Learning Project 2026**

| Author | Email |
|--------|-------|
| Saideep Reddy Tamma | satm25@student.bth.se |
| Sriya Chittaneni | srch25@student.bth.se |
| Meghashyam Sai Dontha | medo25@student.bth.se |

---

## Overview

This project implements and evaluates seven models for marine debris
semantic segmentation on the MARIDA benchmark dataset. We propose
**DeepSpectralUNet** — a novel encoder-decoder architecture that
processes FDI, NDVI, NDWI and FAI spectral indices through a dedicated
multi-scale branch fused at every decoder stage. The model is evaluated
against five baselines including Random Forest, U-Net, Attention U-Net,
DeepLabV3+ and ResAttUNet-CBAM.

---

## Results

| Model | IoU | DebrisF1 | MacroF1 | Accuracy |
|-------|-----|----------|---------|----------|
| Random Forest | 0.6725 | 0.8042 | 0.5620 | 0.9235 |
| U-Net | 0.1900 | 0.3193 | 0.5113 | 0.8876 |
| Attention U-Net | 0.1996 | 0.3327 | 0.5074 | 0.8728 |
| DeepLabV3+ | 0.0671 | 0.1258 | 0.3631 | 0.7179 |
| ResAttUNet-CBAM | 0.4205 | 0.5921 | 0.7477 | 0.9548 |
| SpectralAttUNet | 0.3502 | 0.5188 | 0.6599 | 0.9334 |
| **DeepSpectralUNet (Proposed)** | **0.4264** | **0.5978** | **0.6190** | **0.9350** |

Primary metric is Debris IoU. DeepSpectralUNet achieves best IoU
and DebrisF1 among all deep learning models.

---

## Models

| Model | Type | Parameters |
|-------|------|-----------|
| Random Forest | Classical baseline | N/A |
| U-Net | Deep learning baseline | 31M |
| Attention U-Net | Attention baseline | 31M |
| DeepLabV3+ | Dilated convolution baseline | 16M |
| ResAttUNet-CBAM | State of art Mohammed 2022 | 32.8M |
| SpectralAttUNet | Proposed single-stage fusion | 70.7M |
| DeepSpectralUNet | Proposed multi-scale fusion | 75.7M |

---

## Dataset

**MARIDA** — Marine Debris Archive (Kikaki et al. 2022)

- 1,381 Sentinel-2 patches of size 256×256 pixels
- 11 spectral bands + 4 computed indices = 15 channels total
- 10 merged output classes
- Splits: 694 train / 328 val / 359 test
- Marine debris = only 0.45% of all pixels

### Download Option 1 — Kaggle (faster):

```bash
pip install kaggle

# place kaggle.json in ~/.kaggle/ first
# get it from https://www.kaggle.com/settings → API → Create New Token

kaggle datasets download -d anangfath/marida-marine-debrish-dataset
unzip marida-marine-debrish-dataset.zip -d MARIDA
```

Kaggle link: https://www.kaggle.com/datasets/anangfath/marida-marine-debrish-dataset

### Download Option 2 — Zenodo (official):

```python
import urllib.request
import zipfile

print("Downloading MARIDA — 4.38 GB, this will take a while...")
urllib.request.urlretrieve(
    "https://zenodo.org/record/5151941/files/MARIDA.zip",
    "MARIDA.zip")

print("Extracting...")
with zipfile.ZipFile("MARIDA.zip", "r") as z:
    z.extractall(".")

print("Done. Dataset ready at MARIDA/")
```

Zenodo link: https://zenodo.org/record/5151941

### After downloading place files like this:

```
marine5/
├── MARIDA/
│   ├── patches/    ← satellite image patches
│   └── splits/     ← train_X.txt val_X.txt test_X.txt
```

---

## Project Structure

```
marine5/
├── marine2.ipynb              ← main notebook
├── README.md
├── requirements.txt
├── outputs/
│   ├── checkpoints/           ← saved model weights
│   │   ├── unet_fixed_best.pth
│   │   ├── attunet_fixed_best.pth
│   │   ├── deeplabv3plus_best.pth
│   │   ├── resattunet_cbam_best.pth
│   │   ├── spectral_attunet_best.pth
│   │   └── deep_spectral_unet_best.pth
│   ├── results/               ← saved figures
│   │   ├── fig1_prediction_maps.png
│   │   ├── fig2_confusion_matrix.png
│   │   ├── fig3_per_class_iou.png
│   │   ├── fig4_attention_maps.png
│   │   ├── fig5_spectral_features.png
│   │   └── fig6_training_curves.png
│   └── train_stats.json       ← normalisation statistics
└── MARIDA/
    ├── patches/               ← satellite patches
    └── splits/                ← train/val/test splits
```

---

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.10+ and CUDA 12.0+

---

## Running the Notebook

Open `marine2.ipynb` in Jupyter:

```bash
jupyter notebook marine2.ipynb
```

### To train all models from scratch:

Run all cells top to bottom in order.

Training times on RTX 5060 8GB:

```
Random Forest        →  2 minutes
U-Net                → 35 minutes  (50 epochs)
Attention U-Net      → 35 minutes  (50 epochs)
DeepLabV3+           → 40 minutes  (50 epochs)
ResAttUNet-CBAM      → 70 minutes  (100 epochs)
SpectralAttUNet      → 90 minutes  (100 epochs)
DeepSpectralUNet     → 90 minutes  (100 epochs)
Total                → ~6 hours
```

### To load saved checkpoints (no retraining):

Run cells 1 to 22 to define everything then run the
checkpoint loading cell directly. Takes about 10 minutes.

### To reproduce exact results:

```
1. Download MARIDA dataset
2. Place in MARIDA/ folder as shown above
3. Run cells 1-22
4. Run checkpoint evaluation cell
5. Results match Table III in report
```

---

## Hardware

Tested on:

```
GPU    : NVIDIA GeForce RTX 5060 Laptop GPU 8GB VRAM
CPU    : Intel Core i7
RAM    : 16GB
OS     : Ubuntu 24
Python : 3.13
PyTorch: 2.12.0
CUDA   : 12.8
```

Minimum requirements:

```
GPU    : 6GB VRAM
RAM    : 16GB
Storage: 10GB free (dataset + checkpoints)
```

---

## Key Technical Decisions

| Decision | Choice | Justification |
|----------|--------|---------------|
| Loss function | InvFreqWCE | Automatic class weights, stable training |
| Sampler | WeightedRandomSampler | Debris in every training batch |
| Scheduler | 5-epoch warmup + cosine decay | Prevents early training collapse |
| Input channels | 15 (11 bands + 4 indices) | Kikaki 2022 spectral importance |
| Primary metric | Debris IoU | Standard MARIDA benchmark metric |
| Seed | 42 | Full reproducibility |

---

## Ablation Study

| Model | IoU | DebrisF1 | What changed |
|-------|-----|----------|--------------|
| DeepSpectralUNet | 0.4264 | 0.5978 | Full model |
| SpectralAttUNet | 0.3502 | 0.5188 | Single stage fusion only |

Multi-scale fusion improves IoU by 0.0762 and DebrisF1 by 0.0831.

---

## Known Issues

```
1. Single worker DataLoader required
   rasterio is not fork-safe with multiple workers

2. Minimum 6GB GPU VRAM needed for training
   DeepSpectralUNet with batch size 4

3. Training may be interrupted on low VRAM GPUs
   Checkpoint is saved automatically at best val F1
   Resume from checkpoint without retraining
```

---

## References

```
[1] Kikaki et al. 2022 — MARIDA dataset
    PLOS ONE 17(1): e0262247

[2] Mohammed 2022 — ResAttUNet-CBAM
    arXiv:2210.08506

[3] Bouchelaghem et al. 2026 — InvFreqWCE loss
    Frontiers in Marine Science

[4] Ronneberger et al. 2015 — U-Net
    MICCAI 2015

[5] Oktay et al. 2018 — Attention U-Net
    arXiv:1804.03999

[6] Chen et al. 2018 — DeepLabV3+
    ECCV 2018

[7] Woo et al. 2018 — CBAM
    ECCV 2018

[8] Biermann et al. 2020 — FDI index
    Scientific Reports 10: 5364

[9] Hu 2009 — FAI index
    Remote Sensing of Environment 113: 2118
```

---

## License

Academic project — Blekinge Institute of Technology 2026.
For research and educational use only.
