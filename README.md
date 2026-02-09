# pm25__martin__2dataverse

Pipeline to download Washington University PM2.5 satellite data from Box and upload to Harvard Dataverse.

## Overview

This repository handles data staging for PM2.5 satellite estimates from the [Atmospheric Composition Analysis Group (ACAG)](https://sites.wustl.edu/acag/datasets/surface-pm2-5/) at Washington University. It downloads NetCDF files from Box and uploads them to Harvard Dataverse for downstream processing.

```
Box (ACAG) → Download → Local Storage → Upload → Harvard Dataverse
```

## Supported Datasets

| Dataset | Resolution | Description |
|---------|------------|-------------|
| V5GL04 | 0.10° | Hybrid PM2.5 estimates |
| V5GL0502 | 0.05° | Hybrid PM2.5 estimates (higher resolution) |
| V6GL02 | 0.10° | CNN-based PM2.5 estimates |

Each dataset is available in yearly and monthly temporal frequencies.

## Setup

### 1. Clone and create environment

```bash
git clone https://github.com/NSAPH-Data-Processing/pm25__martin__2dataverse.git
cd pm25__martin__2dataverse

conda env create -f environment.yaml
conda activate pm25_2dataverse
```

### 2. Configure Dataverse credentials

1. Get an API token from [Harvard Dataverse](https://dataverse.harvard.edu) (Account → API Token)
2. Create a dataset on Dataverse for each data type you'll upload
3. Update `conf/datasets/*.yaml` with:
   - Your dataset DOI
   - Your API token

## Usage

### Download from Box

```bash
# Download V5GL04 yearly data (default)
python src/download_from_box.py

# Download specific dataset and frequency
python src/download_from_box.py dataset=V6GL02 temporal_freq=monthly
```

### Upload to Dataverse

```bash
# Upload downloaded files to Dataverse
python src/upload_to_dataverse.py

# Upload specific dataset
python src/upload_to_dataverse.py dataset=V6GL02 temporal_freq=monthly
```

### Full workflow example

```bash


# Download and upload V6GL02 monthly data
python src/download_from_box.py datasets=V6GL02 dataset=V6GL02 temporal_freq=monthly
python src/upload_to_dataverse.py datasets=V6GL02 dataset=V6GL02 temporal_freq=monthly        
```


python src/upload_to_dataverse.py datasets=V6GL02 temporal_freq=monthly
python src/upload_to_dataverse.py datasets=V6GL02 temporal_freq=yearly

python src/upload_to_dataverse.py datasets=V5GL0502 temporal_freq=monthly
python src/upload_to_dataverse.py datasets=V5GL0502 temporal_freq=yearly

python src/upload_to_dataverse.py datasets=V5GL04 temporal_freq=monthly
python src/upload_to_dataverse.py datasets=V5GL04 temporal_freq=yearly


## Configuration

Configuration uses [Hydra](https://hydra.cc/). Main parameters:

| Parameter | Options | Description |
|-----------|---------|-------------|
| `dataset` | V5GL04, V5GL0502, V6GL02 | Which PM2.5 dataset |
| `temporal_freq` | yearly, monthly | Temporal resolution |
| `download_dir` | path | Local storage directory |

Dataset configs are in `conf/datasets/`. Each contains:
- Box URLs for download
- Dataverse DOI and credentials for upload

## Directory Structure

```
pm25__martin__2dataverse/
├── src/
│   ├── download_from_box.py    # Download from ACAG Box
│   └── upload_to_dataverse.py  # Upload to Harvard Dataverse
├── conf/
│   ├── config.yaml             # Main configuration
│   └── datasets/               # Dataset-specific configs
│       ├── V5GL04.yaml
│       ├── V5GL0502.yaml
│       └── V6GL02.yaml
├── data/                       # Downloaded files (gitignored)
├── environment.yaml
└── README.md
```

## References

van Donkelaar, A., Hammer, M.S., Bindle, L., Brauer, M., Brook, J.R., Garay, M.J., Hsu, N.C., Kalashnikova, O.V., Kahn, R.A., Lee, C., Levy, R.C., Lyapustin, A., Sayer, A.M. and Martin, R.V. (2021). Monthly Global Estimates of Fine Particulate Matter and Their Uncertainty. *Environmental Science & Technology*. [doi:10.1021/acs.est.1c05309](https://pubs.acs.org/doi/10.1021/acs.est.1c05309)
