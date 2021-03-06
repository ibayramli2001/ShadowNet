# ShadowNet

This repository contains code for binary damage segmentation networks examined in [this](https://aiforgood2020.github.io/papers/AI4SG_paper_76.pdf) paper. If you use this repository for an academic project, please cite:

> Bayramli, I, Bondi, E., Tambe, M.. In the Shadow of Disaster: Finding Shadows to Improve Damage Detection. Harvard CRCS Workshop on AI for Social Good.

**Abstract:** Rapid damage assessment after natural disasters is crucial for effective planning of relief efforts. Satellites with Very High Resolution (VHR) sensors can provide a detailed aerial image of the affected area, but current damage detection systems are fully- or semi-manual which can delay the delivery of emergency care. In this paper, we apply recent advancements in segmentation and change detection to detect damage given pre- and post-disaster VHR images of an affected area. Moreover, we demonstrate that segmentation models trained for this task rely on shadows by showing that (i) shadows influence false positive detections by the model, and (ii) removing shadows leads to poorer performance. Through this analysis, we aim to inspire future work to improve damage detection.

<p align="center">
  <a href="https://aiforgood2020.github.io/papers/AI4SG_paper_76.pdf">View Paper</a>
</p>

<img align="center" src="img/shadows_replacement.PNG">

<img align="center" src="img/table_shadows.PNG">

### Data

Download the satellite images from [xView2 Challenge website](https://xview2.org/dataset).

### Dependencies
Create a conda environment and install the program dependencies using the following commands:
```
conda create -n shadownet pip
conda install pytorch torchvision -c pytorch
pip install opencv-python numpy mkl-random pandas rasterio matplotlib
```

or install dependencies directly from `requirements.txt`:
```
pip install -r requirements.tx
```

You also should export the global variables in `export_vars.sh` that the programs depend on.

### Credits
In writing this codebase, we have benefited from work of Frontier Development Lab on [Multi3Net](https://github.com/FrontierDevelopmentLab/multi3net) architecture.
